import {ConstraintTemplate, TypeSystem} from "./typesystem";

export interface Module {
    canAssignTo: ConstraintTemplate<CanAssignTo>
}

export interface CanAssignTo {
    from: string,
    to: string
}

/**
 * Builtin constraints for type system.
 */
export default function (typeSystem: TypeSystem): Module {
    return {
        canAssignTo: typeSystem.newConstraint<CanAssignTo>({name: "canAssignTo", data: "CanAssignTo"})
    }
}
