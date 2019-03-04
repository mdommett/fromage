"""
The class represents pairs of Mol objects
"""
import fromage.utils.array_operations as ao
import numpy as np
class Dimer(object):
    """
    Object representing a pair of molecules

    Attributes
    ----------
    mols : list of two Mol objects
        The two molecules constituting the dimer
    alpha, beta, gamma : floats
        The describing angles. alpha is the angle between principal axes,
        beta secondary and gamma perpendicular

    """

    def __init__(self, mols=[]):
        self.mols = mols
        self.alpha = None
        self.beta = None
        self.gamma = None

    def __repr__(self):
        out_str = "Mol A\n" + self.mols[0].__str__() + "Mol B\n" + self.mols[1].__str__()
        return out_str

    def __str__(self):
        return self.__repr__()

    def angles(self):
        """
        Return the three descriptor angles of the dimer

        Returns
        -------
        out_arr : 3 x 1 numpy array
            The three angles alpha, beta, gamma

        """
        if self.mols[0].geom.perp_ax == None:
            self.mols[0].calc_axes()
        if self.mols[1].geom.perp_ax == None:
            self.mols[1].calc_axes()
        out_lis = [ao.vec_angle(self.mols[0].geom.prin_ax,self.mols[1].geom.prin_ax),
                    ao.vec_angle(self.mols[0].geom.sec_ax,self.mols[1].geom.sec_ax),
                    ao.vec_angle(self.mols[0].geom.perp_ax,self.mols[1].geom.perp_ax)]
        out_arr = np.array(out_lis)

        return out_arr

    def calc_angles(self):
        """Set the three descriptor angles"""
        descriptor_angles = self.angles()
        self.alpha = descriptor_angles[0]
        self.beta = descriptor_angles[1]
        self.gamma = descriptor_angles[2]

        return
