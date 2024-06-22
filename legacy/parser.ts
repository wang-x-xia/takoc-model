import {Project} from "ts-morph";
import type {TsElement} from "./core";

/**
 * Parses a TypeScript file and returns a list of elements.
 *
 * @param filePath
 * @returns elements
 */
export function parseTsFile(filePath: string): any[] {
    const project = new Project();
    const sourceFile = project.addSourceFileAtPath(filePath);

    const elements: TsElement[] = [];

    // Extract variables
    sourceFile.getVariableDeclarations().forEach((variable) => {
        elements.push({
            name: variable.getName(),
            type: "variable",
        });
    });

    // Extract types
    sourceFile.getTypeAliases().forEach((typeAlias) => {
        elements.push({
            name: typeAlias.getName(),
            type: "type",
        });
    });

    // Extract function as variable
    sourceFile.getFunctions().forEach((functionDeclaration) => {
        elements.push({
            name: functionDeclaration.getName(),
            type: "variable",
        });
    });

    // Extract class as variable
    sourceFile.getClasses().forEach((classDeclaration) => {
        elements.push({
            name: classDeclaration.getName(),
            type: "variable",
        });
    });

    // Extract interface as type
    sourceFile.getInterfaces().forEach((interfaceDeclaration) => {
        elements.push({
            name: interfaceDeclaration.getName(),
            type: "type",
        });
    })

    // Extract enum as type
    sourceFile.getEnums().forEach((enumDeclaration) => {
        elements.push({
            name: enumDeclaration.getName(),
            type: "type",
        });
    });

    return elements;
}