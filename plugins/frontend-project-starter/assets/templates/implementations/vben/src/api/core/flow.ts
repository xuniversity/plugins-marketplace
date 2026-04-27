export namespace FlowApi {
  export type FlowStatus = 'COMPLETED' | 'FAILED' | 'INITIALIZED' | 'RUNNING';

  export type NodeStatus =
    | 'COMPLETED'
    | 'FAILED'
    | 'REJECTED'
    | 'RUNNING'
    | 'WAITING';

  export interface FlowDefinitionResponse {
    description?: string;
    id: string;
    key?: string;
    name: string;
    nodeDefinitions?: NodeDefinitionResponse[];
  }

  export interface NodeDefinitionResponse {
    description?: string;
    flowDefinitionId?: string;
    id: string;
    metadata?: NodeMetadata;
    name: string;
    nextId?: string;
    previousId?: string;
    type?: 'AUDIT' | 'CONDITION' | 'START';
  }

  export interface NodeMetadata {
    branches?: ConditionalBranch[];
    handlerBean?: string;
    rejectableTargets?: string[];
    roles?: string[];
  }

  export interface ConditionalBranch {
    condition: string;
    name: string;
    targetNodeDefId: string;
  }

  export interface FlowInstanceResponse {
    createdAt?: string;
    createdBy?: string;
    endAt?: string;
    flowDefinition?: FlowDefinitionResponse;
    id: string;
    name: string;
    nodeInstances?: NodeInstanceResponse[];
    startAt?: string;
    status: FlowStatus;
    updatedAt?: string;
    updatedBy?: string;
  }

  export interface NodeInstanceResponse {
    context?: NodeContext;
    endAt?: string;
    flowDefinitionId?: string;
    id: string;
    nodeDefinitionId?: string;
    startAt?: string;
    status: NodeStatus;
  }

  export interface FlowTimelineNodeSummaryResponse {
    endAt?: string;
    id: string;
    nodeName: string;
    opinion?: string;
    startAt?: string;
    status: NodeStatus;
  }

  export interface FlowSummaryResponse {
    currentNodeName?: string;
    displayText?: string;
    flowInstanceId?: string;
    flowName?: string;
    status: FlowStatus;
    timeline?: FlowTimelineNodeSummaryResponse[];
  }

  export interface NodeContext {
    approved?: boolean;
    auditedAt?: string;
    auditorId?: string;
    fromNodeInstanceId?: string;
    opinion?: string;
  }
}
