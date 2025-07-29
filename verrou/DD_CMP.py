#!/usr/bin/python3
import sys

def extractValue(rep):
    with open(rep + "/result.dat") as f:
        lines = f.readlines()
        last_line = lines[-1]
        return float(last_line.split()[1])  # ex: récupère la colonne 2

if __name__ == "__main__":
    if len(sys.argv) == 2:
        print(extractValue(sys.argv[1]))
    elif len(sys.argv) == 3:
        vref = extractValue(sys.argv[1])
        vcur = extractValue(sys.argv[2])
        rel = abs((vref - vcur) / vref)
        if rel < 5e-9:
            sys.exit(0)  # OK
        else:
            sys.exit(1)  # KO
