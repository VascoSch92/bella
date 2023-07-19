""" Functions and classes specifically modelling Riley groups.
"""

import numpy as np
from . import cayley
from . import farey
import functools


class RileyGroup(cayley.GroupCache):
    """ Represents a Riley group.

        A Riley group is a subgroup of PSL(2,C) generated by the matrices X = [[α,1],[0,α*]] and Y = [[β,0],[μ,β*]]
        where α and β are respectively e^(θi) and e^(ηi) and μ is a complex number. Hence X and Y are:
          - parabolic, if θ = 0 and η = 0;
          - elliptic of finite order p and q (resp.), if θ = mπ/p and η = nπ/q;
          - elliptic of infinite order, otherwise;
        or some kind of mix of possiblilities (so X might be parabolic and Y elliptic, for instance).

        In words represented as strings, x and y represent the inverses of X and Y respectively.

    """
    def __init__(self, θ, η, μ, p=np.inf, q=np.inf):
        """ Construct the Riley group on generators of holonomy angle θ and η with parameter μ.

            For the underlying group to know about finite-order generators, set p and q to the orders of X and Y.
        """
        relations = []

        def generator(index, angle, order):
            if order != np.inf:
                relations.append((index,)*order)
            return np.exp(1j*angle)

        self.α = generator(0, θ, p)
        self.β = generator(1, η, q)
        self.μ = μ
        X = np.array([[self.α,1],[0,np.conj(self.α)]])
        Y = np.array([[self.β,0],[self.μ,np.conj(self.β)]])

        super().__init__([X,Y], relations)
        self.generator_map = {'X':0, 'Y':1, 'x':self.gen_to_inv[0], 'y':self.gen_to_inv[1]}

    def string_to_word(self, s):
        """ Produce a word in the GroupCache sense from a string of letters out of X, Y, x, y. """
        return tuple(functools.reduce( (lambda x,y: x + (self.generator_map[y],)), s, tuple()))

    @functools.cache
    def farey_matrix(self, r, s):
        """ Return the r/s-Farey matrix in this group. """
        return self[self.string_to_word(farey.farey_string(r,s))]

    @functools.cache
    def farey_fixed_points(self, r, s):
        """ Return the fixed points of the r/s-Farey matrix in this group. """
        return self.fixed_points(self.farey_matrix(r,s))

    def guess_radial_coordinate(self, ε):
        """ Attempt to guess the Keen-Series coordinate of the group.

            More precisely, iterate over all possible r/s so that the Farey word
            W_r/s has trace in the cone of angle π*ε symmetric about the negative real
            axis; so if ε = 1 we are checking inclusion in our thickened neighbourhoods.
        """
        for (r,s) in farey.walk_tree_bfs():
            v = farey.polynomial_evaluate(r, s, self.α, self.β, self.μ)
            if np.real(v) < -2:
                θ = 2*np.arctan(abs(np.imag(v)/np.real(v)))
                if θ/np.pi < ε:
                    return (r,s)




class ClassicalRileyGroup(RileyGroup):
    """ Represents a Riley group generated by either *finite order* elliptics or parabolics.
    """
    def __init__(self, p, q, μ):
        super().__init__(np.pi/p, np.pi/q, μ, p, q)
