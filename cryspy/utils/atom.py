"""Defines the Atom object"""

import numpy as np
from collections import Counter

from cryspy.utils import per_table as per
from cryspy.fdist import fdist as fd


class Atom(object):
    """
    Object representing an atom.

    Sometimes also used to represent point charges as atoms of element "point".
    Several functions are present like translate or find_centroid.

    Attributes
    ----------
    x,y,z : floats
        Cartesian coordinates
    q : float
        Partial atomic charge
    connectivity : frozenset of tuples
        The set is ((atom kind,connectivity order),amount) and is set via a
        function which takes the connectivity matrix as argument
    kind : tuple
        Tuple of (atom element,connectivity). This defines the kind of atom
    total_e : int
        Atomic number
    valence : int
        Number of valence electrons
    vdw : float
        Van der Waals radius in Angstrom

    """

    def __init__(self, elemIn="H", xIn=0.0, yIn=0.0, zIn=0.0, qIn=0.0, num=1):
        self.elem = elemIn
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.q = 0.0
        self.num = 1
        # The connectivity is a frozenset (because a list would have a built-in ordering)
        # of the tuples of the form (A,N) where A is an tuple of different
        # distances to atoms e.g. ("C",4) if there is a carbon 4 bonds away. N
        # is the amount of carbons 4 bonds away
        self.connectivity = None
        # Kind is a tuple of (elem,connectivity) and as such is enough to define
        # an atom type at least as well as it would be defined in a forcefield
        # e.g. in acrolein: This is a C atom with 1 O 1-away, an H 1-away, a C
        # 1-away, an H 2-away, a C 2-away and 2 H 3-away
        self.kind = None

        # deal with some sneaky int that may be disguised as float
        try:
            self.x = float(xIn)
            self.y = float(yIn)
            self.z = float(zIn)
            self.q = float(qIn)

        except ValueError:
            print("Some coordinates or charges cannot be cast to float!")

        table = per.periodic
        self.at_num = table[self.elem.lower()]["at_num"]
        self.valence_e = table[self.elem.lower()]["valence_e"]
        self.vdw = table[self.elem.lower()]["vdw"]
        self.my_pos = np.array([self.x,self.y,self.z])
        # to string methods to be used mainly for debugging and .qc file
    def __repr__(self):
        return "{:>6} {:10.6f} {:10.6f} {:10.6f} {:10.6f}".format(self.elem, self.x, self.y, self.z, self.q)

    def __str__(self):
        return "{:>6} {:10.6f} {:10.6f} {:10.6f} {:10.6f}".format(self.elem, self.x, self.y, self.z, self.q)

        # equality function
    def __eq__(self, other):
        return self.elem.lower() == other.elem.lower() and self.x == other.x and self.y == other.y and self.z == other.z and self.q == other.q

    def very_close(self, other):
        """Check if two atoms are very close together"""
        thresh = 0.001
        x_cond = abs(self.x - other.x) < thresh
        y_cond = abs(self.y - other.y) < thresh
        z_cond = abs(self.z - other.z) < thresh

        cond = x_cond and y_cond and z_cond
        return cond

    def xyz_str(self):
        """Return a string of the atom in xyz format"""
        return "{:>6} {:10.6f} {:10.6f} {:10.6f}".format(self.elem, self.x, self.y, self.z)

    def dist2(self, x1, y1, z1):
        """Return distance squared of the atom from a point"""
        # Use for no C++ version
#        r = (self.x - x1) ** 2 + (self.y - y1) ** 2 + (self.z - z1) ** 2
        r = fd.dist2(self.x, self.y, self.z, x1, y1, z1)
        return r

    def dist(self, x1, y1, z1):
        """Return distance of the atom from a point"""
        #r = np.sqrt(self.dist2(x1, y1, z1))
        r = fd.dist(self.x, self.y, self.z, x1, y1, z1)
        return r

    def dist_at_general(self, dist_type, other_atom):
        """Return interatomic distance"""
        r = dist_type(other_atom.x, other_atom.y, other_atom.z)
        return r

    def dist_at(self, other_atom):
        """Return interatomic distance"""
        r = self.dist_at_general(self.dist, other_atom)
        return r

    def dist_at2(self, other_atom):
        """Return interatomic distance"""
        r = self.dist_at_general(self.dist2, other_atom)
        return r

    def at_lap(self, other_atom):
        """Return the overlap between vdw radii"""
        r = self.vdw + other_atom.vdw - self.dist_at(other_atom)
        return r

    def dist_lat (self, x1, y1, z1, aVec, bVec, cVec, order = 1):
        """
        Find the shortest distance to a point in a periodic system.

        Parameters
        ----------
        x1,y1,z1 : floats
            Cartesian coordinates of the target point
        aVec,bVec,cVec : 3x1 array-likes
            Unit cell vectors
        order : positive int
            The amount of translations to be considered. Order 1 considers a
            translation by -1, 0 and 1 of each lattice vector and all resulting
            combination. Order 2 is [-2, -1, 0, 1, 2] and so onzx

        Returns
        -------
        rMin : float
            Minimal distance to the point
        x3,y3,z3 : floats
            Coordinates of the closest image to the point

        """

        in_pos = np.array([x1,y1,z1])
        vectors = np.array([aVec,bVec,cVec])
        multipliers = np.arange(-order,order+1)

        # sets comprised of the ranges of lattice vector values
        aSet = [i*vectors[0] for i in multipliers]
        bSet = [i*vectors[1] for i in multipliers]
        cSet = [i*vectors[2] for i in multipliers]

        # minimum r distance
        rMin = float("inf")

        # loop over all possible translations of the input point
        for trans1 in aSet:
            for trans2 in bSet:
                for trans3 in cSet:
                    img_pos = in_pos + trans1 + trans2 + trans3
                    #r=np.linalg.norm(self.my_pos-img_pos)
                    r=self.dist(img_pos[0], img_pos[1], img_pos[2])
                    # if this particular translation of the point is the closest
                    # to the atom so far
                    if r < rMin:
                        rMin = r
                        # image coordinates
                        x3 = img_pos[0]
                        y3 = img_pos[1]
                        z3 = img_pos[2]
        return rMin, x3, y3, z3

    def per_dist(self, other_atom, vectors, order=1, old_pos=False):
        """
        Find the shortest distance to another atom in a periodic system.

        Parameters
        ----------
        other_atom : Atom object
            The atom which to which the distance is being calculated
        vectors : 3 x 3 numpy array
            Unit cell vectors
        order : positive int
            The amount of translations to be considered. Order 1 considers a
            translation by -1, 0 and 1 of each lattice vector and all resulting
            combination. Order 2 is [-2, -1, 0, 1, 2] and so onzx

        Returns
        -------
        r_min : float
            Minimal distance to the point
        at_img : floats (optional)
             Closest image of the atom being targeted

        """
        multipliers = np.arange(-order,order+1)

        # sets comprised of the ranges of lattice vector values
        a_set = [i*vectors[0] for i in multipliers]
        b_set = [i*vectors[1] for i in multipliers]
        c_set = [i*vectors[2] for i in multipliers]

        # minimum r distance
        r_min = float("inf")

        # loop over all possible translations of the input point
        for trans_a in a_set:
            for trans_b in b_set:
                for trans_c in c_set:
                    cell_origin = trans_a + trans_b + trans_c
                    tmp_img_atom = other_atom.v_translated(cell_origin)
                    r = self.dist_at(tmp_img_atom)
                    if r <= r_min:
                        if r == r_min:
                            print("WARNING: the closest periodic image is ill-defined")
                        r_min = r
                        at_img = tmp_img_atom
        if old_pos:
            return r_min, at_img
        else:
            return r_min

    def per_lap(self, other_atom, vectors, order=1, old_pos=False):
        """
        Find the vdw overlap distance to another atom in a periodic system

        Parameters
        ----------
        other_atom : Atom object
            The atom which to which the distance is being calculated
        vectors : 3 x 3 numpy array
            Unit cell vectors
        order : positive int
            The amount of translations to be considered. Order 1 considers a
            translation by -1, 0 and 1 of each lattice vector and all resulting
            combination. Order 2 is [-2, -1, 0, 1, 2] and so onzx

        Returns
        -------
        r_min : float
            Minimal distance to the point
        at_img : floats (optional)
             Closest image of the atom being targeted

        """

        r_min, at_img = self.per_dist(other_atom, vectors, order=order, old_pos = True)

        lap_out = self.vdw + other_atom.vdw - r_min

        if old_pos:
            return lap_out, at_img
        else:
            return lap_out

    def translated(self, x1, y1, z1):
        """Return a new atom which is a translated copy."""
        xout, yout, zout = self.x, self.y, self.z
        xout += x1
        yout += y1
        zout += z1
        outAtom = Atom(self.elem, xout, yout, zout, self.q)
        return outAtom

    def v_translated(self, vec_trans):
        """Return a new atom which is a translated copy."""
        old_pos = np.array([self.x,self.y,self.z])
        new_pos = old_pos+vec_trans
        outAtom = Atom(self.elem, new_pos[0], new_pos[1], new_pos[2], self.q)
        return outAtom

    def translate(self, x1, y1, z1):
        """Translate the atom by some vector."""
        self.x += x1
        self.y += y1
        self.z += z1
        return

    def v_translate(self, vec_trans):
        """Translate the atom by some vector."""
        self.x += vec_trans[0]
        self.y += vec_trans[1]
        self.z += vec_trans[2]
        return

    def set_connectivity(self, in_atoms, in_row):
        """
        Set the connectivity and the kind of the atom.

        This function needs a row of a connectivity matrix which can be obtained
        with functions from assign_charges.py

        Check the constructor at the top of this file for more info on connectivity
        and kind.

        Parameters
        ----------
        in_atoms : list of atoms
            Atoms in the system of which this atom is a part
        in_row : 1-d array-like
            The row of the connectivity matrix of in_atoms which corresponds to
            this atom

        """
        links = []
        for i, atom in enumerate(in_atoms):
            if in_row[i] != 0:
                links.append((in_atoms[i].elem, in_row[i]))
        self.connectivity = frozenset(Counter(links).most_common())
        self.kind = (self.elem, self.connectivity)
        return
