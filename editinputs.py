# functions for editing inputs of various programs

import sys
import numpy
from atom import Atom
from random import randint

# edits a cp2k template file called cp2k.template.in
# and writes a new version called cp2k.[input name].in
# with required lattice vectors and atomic positions


def editcp2k(inName, vectors, atoms):
    with open("cp2k.template.in") as tempFile:
        tempContent = tempFile.readlines()

    # strings for each lattice vector
    aVec = "\t".join(map(str, vectors[0]))
    bVec = "\t".join(map(str, vectors[1]))
    cVec = "\t".join(map(str, vectors[2]))

    cp2kIn = open("cp2k." + inName + ".in", "w")

    for line in tempContent:

        # writes the name of the calculation at the top of the file
        if "XXX__NAME__XXX" in line:
            cp2kIn.write(line.replace("XXX__NAME__XXX", inName))

        # replace the tags with the coordinates of lattice vectors
        elif "XXX__AVEC__XXX" in line:
            cp2kIn.write(line.replace("XXX__AVEC__XXX", aVec))
        elif "XXX__BVEC__XXX" in line:
            cp2kIn.write(line.replace("XXX__BVEC__XXX", bVec))
        elif "XXX__CVEC__XXX" in line:
            cp2kIn.write(line.replace("XXX__CVEC__XXX", cVec))

        # writes atomic coordinates
        # NB, tabs are not sufficient, a blank space is added
        elif "XXX__POS__XXX" in line:
            for atom in atoms:
                #lineStr = "{:>6} {:10.6f} {:10.6f} {:10.6f}".format(atom.elem, atom.x, atom.y, atom.z)
                #cp2kIn.write(lineStr+"\n")
                cp2kIn.write(str(atom.elem) + " \t" + str(atom.x) +
                             " \t" + str(atom.y) + " \t" + str(atom.z) + "\n")

        else:  # if no tag is found
            cp2kIn.write(line)

    tempFile.close()
    cp2kIn.close()
    return

# edits a cp2k submission script template to
# give it the correct job, input and output names
# possibly useless, stored here for later use


def editcp2kSub(inName):
    with open("script-cp2k.template") as tempFile:
        tempContent = tempFile.readlines()

    subScript = open("script-cp2k." + inName, "w")

    for line in tempContent:
        if "XXX__NAME__XXX" in line:
            subScript.write(line.replace("XXX__NAME__XXX", inName))
        else:
            subScript.write(line)

    subScript.close()
    return

# writes an xyz file from a list of atoms


def writexyz(inName, atoms):
    outFile = open(inName + ".xyz", "w")
    outFile.write(str(len(atoms)) + "\n")
    outFile.write(inName + "\n")

    for atom in atoms:
        outFile.write(atom.xyzStr())
    outFile.close()
    return


# writes a .uc file for the Ewald program
# input the name, the matrix of lattice vectors
# each multiplication of cell through a vector
# and a list of Atom objects
def writeuc(inName, vectors, aN, bN, cN, atoms):
    outFile = open(inName + ".uc", "w")
    outFile.write("\t".join(map(str, vectors[0])) + "\t" + str(aN) + "\n")
    outFile.write("\t".join(map(str, vectors[1])) + "\t" + str(bN) + "\n")
    outFile.write("\t".join(map(str, vectors[2])) + "\t" + str(cN) + "\n")

    # Transpose to ge the transformation matrix
    M = numpy.transpose(vectors)
    # Inverse transformation matrix
    U = numpy.linalg.inv(M)

    for atom in atoms:
        dirPos = [atom.x, atom.y, atom.z]
        fracPos = numpy.dot(U, dirPos).tolist()
        for coord in fracPos:
            if coord < 0:
                fracPos[fracPos.index(coord)] = 1 + coord
        strLine = "\t".join(map(str, fracPos)) + "\t" + \
            str(atom.q) + "\t" + str(atom.elem) + "\n"
        outFile.write(strLine)
    outFile.close()
    return

# writes a .qc file for Ewald with a name and a list of atoms


def writeqc(inName, atoms):
    outFile = open(inName + ".qc", "w")
    for atom in atoms:
        outFile.write(str(atom))
    outFile.close()
    return
# writes a ewald.in file from the job name,
# the amount of checkpoints in zone 1 and
# the amount of atoms with constrained charge


def writeEwIn(inName, nChk, nAt):
    outFile = open("ewald.in." + inName, "w")
    outFile.write(inName + "\n")
    outFile.write(str(nChk) + "\n")
    outFile.write(str(nAt) + "\n")
    outFile.write("0\n")
    outFile.close()
    return

# writes a seed file for Ewald


def writeSeed():
    outFile = open("seedfile", "w")
    seed1 = randint(1, 2**31 - 86)
    seed2 = randint(1, 2**31 - 250)
    outFile.write(str(seed1) + " " + str(seed2))
    outFile.close()
# writes a Gaussian input file from a template
# with atoms and point charges as inputs


def writeGauss(inName, atoms, points):
    with open("template.com") as tempFile:
        tempContent = tempFile.readlines()

    outFile = open(inName + ".com", "w")

    for line in tempContent:
        if "XXX__NAME__XXX" in line:
            outFile.write(line.replace("XXX__NAME__XXX", inName))
        elif "XXX__POS__XXX" in line:
            for atom in atoms:
                atomStr = str(atom.elem) + " \t" + str(atom.x) + \
                    " \t" + str(atom.y) + " \t" + str(atom.z) + "\n"
                outFile.write(atomStr)
        elif "XXX__CHARGES__XXX" in line:
            for point in points:
                pointStr = str(point.x) + " \t" + str(point.y) + \
                    " \t" + str(point.z) + " \t" + str(point.q) + "\n"
                outFile.write(pointStr)
        else:
            outFile.write(line)
    outFile.close()
    return
