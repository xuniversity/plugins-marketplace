#!/usr/bin/env node

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { execSync, spawnSync } = require("node:child_process");

function printUsage() {
  console.error(`Usage:
  node export_yunxiao_bugs.js --project-name <name> [options]
  node export_yunxiao_bugs.js --project-id <id> [options]
  node export_yunxiao_bugs.js --project-alias <alias> [options]

Options:
  --project-name <name>      Yunxiao project name
  --project-id <id>          Yunxiao project id
  --project-alias <alias>    Project alias defined in config
  --organization-id <id>     Optional override; defaults to current organization
  --config-file <path>       Optional project config file
  --output-dir <path>        Output root, default: <cwd>/docs/output
  --run-date <YYYY-MM-DD>    Optional run date override
  --page-size <n>            Page size for search_workitems, default: 50
  --max-count <n>            Stop after exporting N bugs
  --unresolved-only          Export unresolved bugs only (default)
  --all-bugs                 Export all bug statuses
  --help                     Show this message
`);
}

function parseArgs(argv) {
  const options = {
    outputDir: path.resolve(process.cwd(), "docs/output"),
    pageSize: 50,
    unresolvedOnly: true,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") {
      options.help = true;
      continue;
    }
    if (token === "--unresolved-only") {
      options.unresolvedOnly = true;
      continue;
    }
    if (token === "--all-bugs") {
      options.unresolvedOnly = false;
      continue;
    }
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) {
      throw new Error(`Missing value for ${token}`);
    }
    if (token === "--project-name") {
      options.projectName = next;
    } else if (token === "--project-id") {
      options.projectId = next;
    } else if (token === "--project-alias") {
      options.projectAlias = next;
    } else if (token === "--organization-id") {
      options.organizationId = next;
    } else if (token === "--config-file") {
      options.configFile = path.resolve(next);
    } else if (token === "--output-dir") {
      options.outputDir = path.resolve(next);
    } else if (token === "--run-date") {
      options.runDate = next;
    } else if (token === "--page-size") {
      options.pageSize = Number(next);
    } else if (token === "--max-count") {
      options.maxCount = Number(next);
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
    index += 1;
  }

  return options;
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function normalizeBaseUrl(value) {
  return String(value || "").replace(/\/+$/, "");
}

function parseSimpleTomlSection(content, sectionName) {
  const sectionHeader = `[${sectionName}]`;
  const values = {};
  let insideSection = false;

  for (const rawLine of String(content || "").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) {
      continue;
    }
    if (line.startsWith("[") && line.endsWith("]")) {
      insideSection = line === sectionHeader;
      continue;
    }
    if (!insideSection) {
      continue;
    }

    const match = line.match(/^([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$/);
    if (!match) {
      continue;
    }

    const [, key, rawValue] = match;
    values[key] = rawValue
      .replace(/\\"/g, '"')
      .replace(/\\\\/g, "\\")
      .replace(/\\n/g, "\n")
      .replace(/\\t/g, "\t");
  }

  return values;
}

function resolveCodexConfigPath() {
  const codexHome = process.env.CODEX_HOME || path.join(os.homedir(), ".codex");
  return path.join(codexHome, "config.toml");
}

function loadYunxiaoEnvFallback() {
  const configPath = resolveCodexConfigPath();
  if (!fs.existsSync(configPath)) {
    return { configPath, values: {} };
  }

  const content = fs.readFileSync(configPath, "utf8");
  const values = parseSimpleTomlSection(content, "mcp_servers.yunxiao.env");
  return { configPath, values };
}

function ensureYunxiaoSetting(name, fallbackValues, configPath) {
  const envValue = process.env[name];
  if (envValue) {
    return envValue;
  }

  const fallbackValue = fallbackValues?.[name];
  if (fallbackValue) {
    process.env[name] = fallbackValue;
    return fallbackValue;
  }

  const fallbackHint = configPath
    ? ` or configure it under [mcp_servers.yunxiao.env] in ${configPath}`
    : "";
  throw new Error(`Missing required environment variable: ${name}${fallbackHint}`);
}

function loadSdk() {
  const npmRoot = execSync("npm root -g", { encoding: "utf8" }).trim();
  const sdkRoot = path.join(
    npmRoot,
    "alibabacloud-devops-mcp-server",
    "node_modules",
    "@modelcontextprotocol",
    "sdk",
    "dist",
    "cjs",
  );
  return {
    Client: require(path.join(sdkRoot, "client", "index.js")).Client,
    StdioClientTransport: require(path.join(sdkRoot, "client", "stdio.js")).StdioClientTransport,
  };
}

function pickTextContent(result) {
  if (!result || !Array.isArray(result.content)) {
    throw new Error("Tool result did not contain content");
  }
  const text = result.content
    .filter((item) => item && item.type === "text")
    .map((item) => item.text)
    .join("\n")
    .trim();
  if (!text) {
    throw new Error("Tool result text content was empty");
  }
  return text;
}

function parseJsonToolResult(result, toolName) {
  const text = pickTextContent(result);
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(`Failed to parse JSON from ${toolName}: ${text.slice(0, 400)}`);
  }
}

const DEFAULT_EXCLUDED_STATUS_NAMES = new Set([
  "已修复",
  "已关闭",
  "已解决",
  "暂不修复",
  "暂不解决",
  "延期修复",
  "Deferred Fix",
]);
const DEFAULT_EXCLUDED_STATUS_IDS = new Set(["29", "34", "100085"]);

function getStatusName(item) {
  return String(item?.status?.displayName || item?.status?.name || "").trim();
}

function getStatusId(item) {
  const value = item?.status?.id;
  return value === undefined || value === null ? "" : String(value).trim();
}

function isExcludedStatus(item, excludedStatuses) {
  const statusName = getStatusName(item);
  const statusId = getStatusId(item);
  const normalizedName = statusName.toLowerCase();
  const explicitStatuses = (excludedStatuses || []).map((value) => String(value).trim()).filter(Boolean);
  if (explicitStatuses.length > 0) {
    return explicitStatuses.includes(statusName) || explicitStatuses.includes(statusId);
  }
  return (
    DEFAULT_EXCLUDED_STATUS_NAMES.has(statusName) ||
    DEFAULT_EXCLUDED_STATUS_IDS.has(statusId) ||
    normalizedName.includes("fixed") ||
    normalizedName.includes("closed") ||
    normalizedName.includes("resolved") ||
    normalizedName.includes("deferred") ||
    normalizedName.includes("wontfix") ||
    normalizedName.includes("won't fix")
  );
}

function chooseProject(projects, requestedName) {
  if (!Array.isArray(projects) || projects.length === 0) {
    throw new Error(`No Yunxiao project matched: ${requestedName}`);
  }
  const exact = projects.find((item) => item.name === requestedName);
  if (exact) {
    return exact;
  }
  if (projects.length === 1) {
    return projects[0];
  }
  const names = projects.map((item) => `${item.name} (${item.id})`).join(", ");
  throw new Error(`Multiple projects matched "${requestedName}": ${names}`);
}

function resolveConfigFilePath(requestedPath) {
  const candidates = [];
  if (requestedPath) {
    candidates.push(requestedPath);
  }
  if (process.env.YUNXIAO_BUG_EXPORT_CONFIG) {
    candidates.push(path.resolve(process.env.YUNXIAO_BUG_EXPORT_CONFIG));
  }
  candidates.push(path.resolve(process.cwd(), ".codex/yunxiao-bug-export.projects.json"));
  candidates.push(path.resolve(__dirname, "..", "projects.json"));

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }
  return requestedPath || null;
}

function loadProjectConfig(configFile) {
  if (!configFile) {
    return { path: null, data: null };
  }
  if (!fs.existsSync(configFile)) {
    throw new Error(`Project config file not found: ${configFile}`);
  }
  const data = JSON.parse(fs.readFileSync(configFile, "utf8"));
  if (!data || typeof data !== "object") {
    throw new Error(`Invalid project config file: ${configFile}`);
  }
  if (data.projects !== undefined && (typeof data.projects !== "object" || Array.isArray(data.projects))) {
    throw new Error(`"projects" must be an object in ${configFile}`);
  }
  return { path: configFile, data };
}

function resolveConfiguredProject(options, config) {
  const projects = config?.projects || {};
  if (options.projectAlias) {
    const selected = projects[options.projectAlias];
    if (!selected) {
      throw new Error(`Project alias not found in config: ${options.projectAlias}`);
    }
    return { alias: options.projectAlias, ...selected };
  }
  if (!options.projectId && !options.projectName) {
    if (config?.defaultProjectAlias && projects[config.defaultProjectAlias]) {
      return { alias: config.defaultProjectAlias, ...projects[config.defaultProjectAlias] };
    }
    const aliases = Object.keys(projects);
    if (aliases.length === 1) {
      return { alias: aliases[0], ...projects[aliases[0]] };
    }
  }
  return null;
}

function normalizePerson(value) {
  if (!value) {
    return value;
  }
  const displayName = value.displayName || value.name || value.username || value.userName || null;
  return {
    ...value,
    displayName,
  };
}

function normalizeStatus(value) {
  if (!value) {
    return value;
  }
  return {
    ...value,
    displayName: value.displayName || value.name || null,
  };
}

function parseSerial(serialNumber, projectCustomCode) {
  if (typeof serialNumber === "string") {
    const match = serialNumber.match(/^([A-Za-z0-9_]+)-(\d+)$/);
    if (match) {
      return {
        serialNumber: Number(match[2]),
        rawSerialNumber: serialNumber,
        customCode: projectCustomCode || match[1],
      };
    }
    if (/^\d+$/.test(serialNumber)) {
      return {
        serialNumber: Number(serialNumber),
        rawSerialNumber: `${projectCustomCode || "WORKITEM"}-${serialNumber}`,
        customCode: projectCustomCode || "WORKITEM",
      };
    }
    return {
      serialNumber,
      rawSerialNumber: serialNumber,
      customCode: projectCustomCode || "WORKITEM",
    };
  }
  if (typeof serialNumber === "number") {
    return {
      serialNumber,
      rawSerialNumber: `${projectCustomCode || "WORKITEM"}-${serialNumber}`,
      customCode: projectCustomCode || "WORKITEM",
    };
  }
  return {
    serialNumber,
    rawSerialNumber: null,
    customCode: projectCustomCode || "WORKITEM",
  };
}

function buildPlainTextDocument(description) {
  const raw = String(description || "").trim();
  if (!raw) {
    return {
      htmlValue: "",
      jsonMLValue: [],
    };
  }
  if (raw.includes("<") && raw.includes(">")) {
    return {
      htmlValue: raw,
      jsonMLValue: [],
    };
  }
  const paragraphs = raw
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => `<p><span>${escapeHtml(line)}</span></p>`)
    .join("");
  return {
    htmlValue: `<article class="4ever-article">${paragraphs}</article>`,
    jsonMLValue: [],
  };
}

function normalizeDescriptionPayload(description) {
  if (typeof description !== "string") {
    return buildPlainTextDocument("");
  }
  const raw = description.trim();
  if (!raw) {
    return buildPlainTextDocument("");
  }
  if (raw.startsWith("{") || raw.startsWith("[")) {
    try {
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === "object" && (parsed.htmlValue || parsed.jsonMLValue)) {
        return parsed;
      }
    } catch (_error) {
      // fall through
    }
  }
  return buildPlainTextDocument(raw);
}

function collectSrcs(node, urls) {
  if (!node) {
    return;
  }
  if (Array.isArray(node)) {
    for (const item of node) {
      collectSrcs(item, urls);
    }
    return;
  }
  if (typeof node === "object") {
    if (typeof node.src === "string" && !urls.includes(node.src)) {
      urls.push(node.src);
    }
    for (const value of Object.values(node)) {
      collectSrcs(value, urls);
    }
  }
}

function extractImageUrls(payload) {
  const urls = [];
  collectSrcs(payload?.jsonMLValue || [], urls);
  if (urls.length > 0) {
    return urls;
  }
  const htmlValue = String(payload?.htmlValue || "");
  const regex = /<img[^>]+src="([^"]+)"/g;
  let match;
  while ((match = regex.exec(htmlValue)) !== null) {
    if (!urls.includes(match[1])) {
      urls.push(match[1]);
    }
  }
  return urls;
}

function extractFileIdentifier(url) {
  try {
    const parsed = new URL(url);
    return parsed.searchParams.get("fileIdentifier");
  } catch (_error) {
    return null;
  }
}

function normalizeSuffix(fileInfo) {
  let suffix = fileInfo?.suffix || path.extname(fileInfo?.name || "");
  if (!suffix) {
    return "";
  }
  if (!suffix.startsWith(".")) {
    suffix = `.${suffix}`;
  }
  return suffix.toLowerCase();
}

function sanitizeFileStem(value) {
  return String(value || "bug")
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/-{2,}/g, "-")
    .replace(/^-+|-+$/g, "");
}

async function downloadFile(url, destination) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download ${url}: ${response.status} ${response.statusText}`);
  }
  const buffer = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(destination, buffer);
}

function buildListReference(project, options) {
  const params = new URLSearchParams({
    projectId: project.id,
    projectName: project.name,
  });
  if (options.projectAlias) {
    params.set("projectAlias", options.projectAlias);
  }
  if (options.unresolvedOnly) {
    params.set("unresolvedOnly", "true");
  }
  if (options.maxCount) {
    params.set("maxCount", String(options.maxCount));
  }
  return `yunxiao-mcp://bugs/export?${params.toString()}`;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    printUsage();
    return;
  }
  if (!Number.isInteger(options.pageSize) || options.pageSize <= 0) {
    throw new Error("--page-size must be a positive integer");
  }
  if (options.maxCount !== undefined && (!Number.isInteger(options.maxCount) || options.maxCount <= 0)) {
    throw new Error("--max-count must be a positive integer");
  }

  const configFile = resolveConfigFilePath(options.configFile);
  const loadedConfig = loadProjectConfig(configFile);
  const configuredProject = resolveConfiguredProject(options, loadedConfig.data);

  const requestedProjectId = options.projectId || configuredProject?.projectId;
  const requestedProjectName = options.projectName || configuredProject?.projectName;
  const selectedExcludedStatuses =
    configuredProject?.excludedStatuses || configuredProject?.openStatuses || null;
  options.projectAlias = options.projectAlias || configuredProject?.alias || null;

  if (!requestedProjectName && !requestedProjectId) {
    throw new Error(
      "Specify --project-id, --project-name, or --project-alias. You can also set defaultProjectAlias in the project config file.",
    );
  }

  const { configPath: codexConfigPath, values: yunxiaoEnvFallback } = loadYunxiaoEnvFallback();
  const accessToken = ensureYunxiaoSetting(
    "YUNXIAO_ACCESS_TOKEN",
    yunxiaoEnvFallback,
    codexConfigPath,
  );
  const baseUrl = normalizeBaseUrl(
    ensureYunxiaoSetting("YUNXIAO_API_BASE_URL", yunxiaoEnvFallback, codexConfigPath),
  );
  process.env.YUNXIAO_ACCESS_TOKEN = accessToken;
  process.env.YUNXIAO_API_BASE_URL = baseUrl;

  const { Client, StdioClientTransport } = loadSdk();
  const client = new Client({ name: "yunxiao-bug-export", version: "1.0.0" });
  const transport = new StdioClientTransport({
    command: "alibabacloud-devops-mcp-server",
    env: {
      YUNXIAO_ACCESS_TOKEN: accessToken,
      YUNXIAO_API_BASE_URL: baseUrl,
      FASTMCP_LOG_LEVEL: process.env.FASTMCP_LOG_LEVEL || "ERROR",
    },
    stderr: "pipe",
  });

  const stderrChunks = [];
  transport.stderr?.on("data", (chunk) => {
    stderrChunks.push(String(chunk));
  });

  const callJsonTool = async (name, args) => {
    const result = await client.callTool({ name, arguments: args });
    return parseJsonToolResult(result, name);
  };

  try {
    await client.connect(transport);

    const organizationId =
      options.organizationId ||
      configuredProject?.organizationId ||
      (await callJsonTool("get_current_organization_info", {})).lastOrganization;
    if (!organizationId) {
      throw new Error("Could not resolve organizationId from Yunxiao");
    }

    let project;
    if (requestedProjectId) {
      project = await callJsonTool("get_project", {
        organizationId,
        id: requestedProjectId,
      });
    } else {
      const projects = await callJsonTool("search_projects", {
        organizationId,
        name: requestedProjectName,
        page: 1,
        perPage: 50,
      });
      project = chooseProject(projects, requestedProjectName);
    }
    if (configuredProject?.customCode && !project.customCode) {
      project.customCode = configuredProject.customCode;
    }

    console.error(
      `[yunxiao-bug-export] exporting project ${project.name} (${project.id})` +
        (options.projectAlias ? ` [alias:${options.projectAlias}]` : "") +
        (options.unresolvedOnly ? " [unresolved-only]" : " [all-bugs]"),
    );
    if (loadedConfig.path) {
      console.error(`[yunxiao-bug-export] project config: ${loadedConfig.path}`);
    }

    const listItems = [];
    let page = 1;
    while (true) {
      const result = await callJsonTool("search_workitems", {
        organizationId,
        spaceType: "Project",
        spaceId: project.id,
        category: "Bug",
        page,
        perPage: options.pageSize,
        includeDetails: true,
      });

      listItems.push(...(result.items || []));
      const pagination = result.pagination || {};
      if (!pagination.nextPage || page >= pagination.totalPages) {
        break;
      }
      page = pagination.nextPage;
    }

    let filteredItems = options.unresolvedOnly
      ? listItems.filter((item) => !isExcludedStatus(item, selectedExcludedStatuses))
      : listItems;
    if (options.maxCount) {
      filteredItems = filteredItems.slice(0, options.maxCount);
    }

    const runDate =
      options.runDate ||
      new Date().toLocaleDateString("en-CA", {
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      });
    const runDir = path.join(options.outputDir, "yunxiao-bugs", runDate);
    const imagesDir = path.join(runDir, "yunxiao-bug-images");
    fs.rmSync(imagesDir, { recursive: true, force: true });
    fs.mkdirSync(imagesDir, { recursive: true });

    const imageMap = {};
    const fullItems = [];

    for (let index = 0; index < filteredItems.length; index += 1) {
      const listItem = filteredItems[index];
      console.error(
        `[yunxiao-bug-export] ${index + 1}/${filteredItems.length} ${listItem.serialNumber} ${listItem.subject}`,
      );
      const detail = await callJsonTool("get_work_item", {
        organizationId,
        workItemId: listItem.id,
      });
      const attachments = await callJsonTool("list_workitem_attachments", {
        organizationId,
        workItemId: listItem.id,
      });

      const serialInfo = parseSerial(detail.serialNumber, project.customCode);
      const payload = normalizeDescriptionPayload(detail.description);
      const imageUrls = extractImageUrls(payload);

      for (let imageIndex = 0; imageIndex < imageUrls.length; imageIndex += 1) {
        const imageUrl = imageUrls[imageIndex];
        if (imageMap[imageUrl]) {
          continue;
        }
        const fileIdentifier = extractFileIdentifier(imageUrl);
        if (!fileIdentifier) {
          continue;
        }
        const fileInfo = await callJsonTool("get_workitem_file", {
          organizationId,
          workitemId: listItem.id,
          id: fileIdentifier,
        });
        const fileName =
          `${sanitizeFileStem(serialInfo.rawSerialNumber || serialInfo.serialNumber || listItem.id)}` +
          `-desc-${imageIndex + 1}-${fileIdentifier}${normalizeSuffix(fileInfo)}`;
        const localPath = path.join(imagesDir, fileName);
        await downloadFile(fileInfo.url, localPath);
        imageMap[imageUrl] = {
          localPath: path.resolve(localPath),
          fileId: fileIdentifier,
        };
      }

      fullItems.push({
        id: listItem.id,
        workitem: {
          result: {
            ...detail,
            serialNumber: serialInfo.serialNumber,
            rawSerialNumber: serialInfo.rawSerialNumber,
            status: normalizeStatus(detail.status),
            creator: normalizePerson(detail.creator),
            assignedTo: normalizePerson(detail.assignedTo),
            modifier: normalizePerson(detail.modifier),
            verifier: normalizePerson(detail.verifier),
            space: {
              ...(detail.space || {}),
              id: detail.space?.id || project.id,
              name: detail.space?.name || project.name,
              customCode: detail.space?.customCode || serialInfo.customCode || project.customCode || "WORKITEM",
            },
            document: {
              ...(detail.document || {}),
              content: JSON.stringify(payload),
            },
          },
        },
        attachments: {
          result: Array.isArray(attachments) ? attachments : attachments?.items || attachments?.result || [],
        },
      });
    }

    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "yunxiao-bug-export-"));
    const listCacheFile = path.join(tempDir, "list-cache.json");
    const fullJsonFile = path.join(tempDir, "full-items.json");
    const imageMapFile = path.join(tempDir, "image-map.json");
    fs.writeFileSync(listCacheFile, `${JSON.stringify(filteredItems, null, 2)}\n`);
    fs.writeFileSync(fullJsonFile, `${JSON.stringify(fullItems, null, 2)}\n`);
    if (Object.keys(imageMap).length > 0) {
      fs.writeFileSync(imageMapFile, `${JSON.stringify(imageMap, null, 2)}\n`);
    }

    const materializer = path.join(__dirname, "materialize_yunxiao_bugs.py");
    const commandArgs = [
      materializer,
      "--list-url",
      buildListReference(project, options),
      "--output-dir",
      options.outputDir,
      "--list-cache-file",
      listCacheFile,
      "--full-json-file",
      fullJsonFile,
      "--run-date",
      runDate,
      "--source",
      "yunxiao-mcp",
    ];
    if (Object.keys(imageMap).length > 0) {
      commandArgs.push("--image-map-file", imageMapFile);
    }

    const materialize = spawnSync("python3", commandArgs, {
      stdio: "inherit",
    });
    if (materialize.status !== 0) {
      throw new Error(`materialize_yunxiao_bugs.py exited with code ${materialize.status}`);
    }

    const exportContextFile = path.join(runDir, "export-context.json");
    fs.writeFileSync(
      exportContextFile,
      `${JSON.stringify(
        {
          organizationId,
          projectId: project.id,
          projectName: project.name,
          projectAlias: options.projectAlias,
          configFile: loadedConfig.path,
          projectCustomCode: project.customCode || null,
          unresolvedOnly: options.unresolvedOnly,
          excludedStatuses: selectedExcludedStatuses || Array.from(DEFAULT_EXCLUDED_STATUS_NAMES),
          exportedCount: filteredItems.length,
        },
        null,
        2,
      )}\n`,
    );

    console.log("Export complete:");
    console.log(`  run dir:         ${runDir}`);
    console.log(`  export context:  ${exportContextFile}`);
    console.log(`  image count:     ${Object.keys(imageMap).length}`);
    console.log(`  bug count:       ${filteredItems.length}`);
  } catch (error) {
    const stderrTail = stderrChunks.join("").trim();
    if (stderrTail) {
      console.error(stderrTail);
    }
    throw error;
  } finally {
    await transport.close();
  }
}

main().catch((error) => {
  console.error(`[yunxiao-bug-export] ${error.message}`);
  process.exit(1);
});
