import {Project} from "ts-morph";
import type {TypeScriptGeneratedFunction} from "./core";


export function replaceGeneratedMethod(filePath: string, generated: TypeScriptGeneratedFunction): void {
    const project = new Project()
    const sourceFile = project.addSourceFileAtPath(filePath)
    const functionDeclaration = sourceFile.getFunction(generated["name"])
    sourceFile.replaceText([functionDeclaration.getNonWhitespaceStart(), functionDeclaration.getEnd()], generated["declaration"])
    sourceFile.saveSync();
}