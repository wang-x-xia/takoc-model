export type TypescriptElementType = "variable" | "type"


export function createTypescriptElementType(value: TypescriptElementType): TypescriptElementType {
    if (!["variable", "type"].includes(value)) {
        throw new Error("Unknown Literal Value")
    }
    return value
}

export interface TypescriptElement {
    name: string,
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