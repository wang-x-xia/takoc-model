import {Project} from "ts-morph";
import type {
    TypescriptElement,
    TypeScriptGeneratedFunction,
    TypescriptInterfaceFieldsConstructor,
    TypescriptLiteralType
} from "./core";


export function generateConstructorMethodForTypescriptLiteralType(
    element: TypescriptElement,
    type: TypescriptLiteralType): TypeScriptGeneratedFunction {
    const functionName = "create" + element.name
    const body = `export function ${functionName}(value: ${element.name}): ${element.name} {
    if (!${JSON.stringify(type.values)}.includes(value)) {
        throw new Error("Unknown Literal Value")
    }
    return value
}`
    return {
        name: functionName,
        declaration: body,
    }
}


export function generateConstructorMethodForTypescriptString(
    element: TypescriptElement,
    checker: TypescriptElement): TypeScriptGeneratedFunction {
    const functionName = "create" + element.name
    const body = `export function ${functionName}(value: string): ${element["name"]} {
    if (!${checker.name}(value)) {
        throw new Error("Unmatched String Value")
    }
    return value
}`
    return {
        name: functionName,
        declaration: body,
    }
}


export function generateConstructorMethodForTypescriptInterface(
    element: TypescriptElement,
    fieldsConstructor: TypescriptInterfaceFieldsConstructor): TypeScriptGeneratedFunction {
    const functionName = "create" + element.name
    const body = `export function ${functionName}(value: ${element["name"]}): ${element["name"]} {
    const result = {
${fieldsConstructor.fields.map(field => {
        if (field.method) {
            return "        " + field["name"] + ": " + field["method"]["name"] + "(value." + field["name"] + ")"
        } else {
            return "        " + field["name"] + ": " + "value." + field["name"]
        }
    }).join(",\n")}
    }
    return Object.freeze(result)
}`
    return {
        name: functionName,
        declaration: body,
    }
}


export function replaceGeneratedMethod(filePath: string, generated: TypeScriptGeneratedFunction): void {
    const project = new Project()
    const sourceFile = project.addSourceFileAtPath(filePath)
    const functionDeclaration = sourceFile.getFunction(generated["name"])
    sourceFile.replaceText([functionDeclaration.getNonWhitespaceStart(), functionDeclaration.getEnd()], generated["declaration"])
    sourceFile.saveSync();
}