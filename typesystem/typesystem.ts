export interface TypeSystem {

    newType(type: { name: string, description?: string }): void;

    canAssignTo(assignTo: { assign: string, to: string, description?: string }): void;
}
