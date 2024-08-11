import {TypeNode} from "ts-morph";
import type {TypescriptElement, TypescriptFile, TypescriptFilePath} from "./core";
import {findElement} from "./file";
import {readTypescriptFile} from "./parser";


export function extractCheckerFunction(
    filePath: TypescriptFilePath,
    element: TypescriptElement,
    file: TypescriptFile,
): TypescriptElement | undefined {
    if (element.type !== "variable") {
        return undefined
    }
    const sourceFile = readTypescriptFile(filePath)
    const functionDeclaration = sourceFile.getFunction(element.name)
    if (functionDeclaration === undefined) {
        return undefined
    }
    const parameters = functionDeclaration.getParameters()
    if (parameters.length !== 1) {
        // Only 1 parameter is needed for checker
        return undefined
    }

    const returnType = functionDeclaration.getReturnTypeNode()
    if (returnType === undefined) {
        return undefined
    }
    if (!TypeNode.isTypePredicate(returnType)) {
        return undefined
    }
    const param = returnType.getParameterNameNode()
    if (!TypeNode.isIdentifier(param)) {
        return undefined
    }
    // Due to only 1 parameter, we can ignore the name check.
    const assertType = returnType.getTypeNode()
    if (!TypeNode.isTypeReference(assertType)) {
        return undefined
    }
    return findElement(file, assertType.getText(), "type")
}