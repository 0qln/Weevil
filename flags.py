import sys

def getFlags(argv, idx) -> []:
    flagIndecies = []
    while (idx < len(argv) and isFlag(argv, idx)):
        flagIndecies.append(idx)
        idx += 1
    return flagIndecies

def isFlag(argv, idx) -> bool:
    return argv[idx][0] == '-'

def getValue(input, targetFlag):
    return input.replace(targetFlag + '=', '')