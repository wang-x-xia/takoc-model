import type {TypescriptElement, TypescriptElementType, TypescriptFile, TypescriptIdentifier} from "./core";


export function findElement(file: TypescriptFile, name: TypescriptIdentifier, type: TypescriptElementType): TypescriptElement | undefined {
    return file.elements.find(element => element.name === name && element.type === type)
}