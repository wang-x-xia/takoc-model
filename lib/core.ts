export type TypescriptElementType = "variable" | "type"


export function createTypescriptElementType(value: TypescriptElementType): TypescriptElementType {
    if (!["variable","type"].includes(value)) {
        throw new Error("Unknown Literal Value")
    }
    return value
}


export type TypescriptIdentifier = string


export function checkTypescriptIdentifier(value: string): value is TypescriptIdentifier {
    const regex = /[$_\p{ID_Start}][$\u200c\u200d\p{ID_Continue}]*/u
    return regex.test(value)
}

export function createTypescriptIdentifier(value: string): TypescriptIdentifier {
    if (!checkTypescriptIdentifier(value)) {
        throw new Error("Unmatched String Value")
    }
    return value
}

export interface TypescriptElement {
    name: TypescriptIdentifier,
    type: TypescriptElementType,
}

export type TypescriptLiteralValue = number | string

export interface TypescriptLiteralType {
    values: TypescriptLiteralValue[]
}


export interface TypeScriptGeneratedFunction {
    name: string,
    declaration: string,
}