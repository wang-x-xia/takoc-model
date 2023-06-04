import {Module} from "./builtin";

export interface TypeSystem extends ModuleTypeSystem<Module> {

    newType(type: { name: string, description?: string }): void;

    /**
     * Create new constraint with parameter type
     */
    newConstraint<T>(constraint: { name: string, data: string }): ConstraintTemplate<T>

    loadModule<T>(module: (typeSystem: TypeSystem) => T): ModuleTypeSystem<T>
}

/**
 * Type hint for constraint.
 */
export type ConstraintTemplate<T> = {}

export type LoadFromTemplate<T> = T extends ConstraintTemplate<infer P> ? P : `ERROR`

/**
 * Signature of create a new constraint
 */
export type ConstraintMethod<T> = (data: T) => void

/**
 * Module Type System to link type between modules
 */
export type ModuleTypeSystem<T> = Record<keyof T, ConstraintMethod<LoadFromTemplate<T[keyof T]>>>
