#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 12:18:04 2022

@author: nwx
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from syndat import sample_widths
from syndat import sample_levels
from syndat import scattering_theory
import pandas as pd


class particle_pair:
    """
    _summary_

    _extended_summary_

    Methods
    -------
    quant_vec_sum: 
        Calculates the quantum vector sum of two angular momenta.
    map_quantum_numbers:
        Maps the possible quantum numbers for pair.
    sample_all_Jpi:
        Samples a full resonance parameter ladder for each possible spin group.
    """

    def __init__(self, ac, M, m, I, i, l_max):
        """
        Initialization of particle pair object for a given reaction.

        The particle_pair class houses information about the incident and target particle for a reaction of interest. 
        The methods for this class include functions to calculate the open channels 

        Parameters
        ----------
        ac : float
            Scattering channel radius in 1e-12 cm.
        M : float or int
            Mass of the target nucleus.
        m : float or int
            Mass of the incident particle.
        I : float or int
            Spin and parity of the target particle.
        i : float or int
            Spin and parity of the incident particle.
        l_max : int
            Highest order waveform to consider (l-value).
        """

        # assuming boundary condition selected s.t. shift factor is eliminated for s wave but not others!

        if ac < 1e-7:
            print("WARNING: scattering radius seems to be given in fm rather than m")

        self.ac = ac # 6.7e-15 # m or 6.7 femtometers
        self.M = M # amu
        self.m = m # 1
        self.I = I
        self.i = i
        self.l_max = l_max

        # generalized
        ac_expected = (1.23*M**(1/3))+0.8 # fermi or femtometers

        # constants
        self.hbar = 6.582119569e-16 # eV-s
        self.c = 2.99792458e8 # m/s
        self.m_eV = 939.565420e6 # eV/c^2


    def quant_vec_sum(self, a,b):
        """
        Calculates a quantum vector sum.

        This function performs a quantum vector sum, a.k.a. it maps the quantum 
        triangular relationship between two integers or half integers.

        Parameters
        ----------
        a : float or int
            a variable.
        b : float or int
            a variable.

        Returns
        -------
        numpy.ndarray
            Array of all possible quantum values.
        """
        a = abs(a); b=abs(b)
        vec = np.arange(abs(a-b), a+b+1, 1)
        return vec


    def map_quantum_numbers(self, print_out):
        """
        Maps the possible quantum numbers for pair.

        This function maps out the possible quantum spin numbers (Jpi) for a given
        particle pair up to some maximum considered incident waveform (l-wave).

        Parameters
        ----------
        particle_pair : syndat object
            Particle_pair object containing information about the reaction being studied.
        print_out : bool
            User option to print out quantum spin (J) mapping to console.

        Returns
        -------
        Jn : array-like
            List containing possible J, # of contibuting channels, and contibuting 
            waveforms for negative parity. Formatted as (J,#chs,[l-wave, l-wave])
        Jp : array-like
            List containing possible J, # of contibuting channels, and contibuting 
            waveforms for positive parity. Formatted as (J,#chs,[l-wave, l-wave])
        Notes
        -----
        
        Examples
        --------
        >>> from sample_resparm import sample_spin_groups
        >>> sample_spin_groups.map_quantum_numbers(3/2,1/2,2, False)
        ([(1.0, 1, [0.0]), (2.0, 1, [0.0])],
        [(0.0, 1, [1.0]),
        (1.0, 2, [1.0, 1.0]),
        (2.0, 2, [1.0, 1.0]),
        (3.0, 1, [1.0])])
        """
        
        # define object atributes
        I = self.I
        i = self.i
        l_wave_max = self.l_max

        # now perform calculations
        Jn = []; Jp = []
        S = self.quant_vec_sum(I,i)
        L = range(l_wave_max+1)

        i_parity = (-1 if i<0 else 1)
        I_parity = (-1 if I<0 else 1)
        S_parity = i_parity*I_parity

        possible_Jpi = {}
        J_negative = []; J_positive = []
        for i_l, l in enumerate(L):
            this_l = {}
            
            l_parity = (-1)**l
            J_parity = S_parity*l_parity
            
            for i_s, s in enumerate(S):
                js = self.quant_vec_sum(s,l)
                this_l[f's={s}'] = js
                for j in js:
                    if J_parity == 1:
                        J_positive.append([l,s,j])
                    if J_parity == -1:
                        J_negative.append([l,s,j])
                
            possible_Jpi[f'l={l}'] = this_l
                
        if len(J_negative) > 0:
            Jn_total = np.array(J_negative)
            Jn_unique = np.unique(Jn_total[:,2])

            for j in Jn_unique:
                entrance_channels = np.count_nonzero(Jn_total[:,2] == j)
                
                ls = []; ss = []
                for i, jtot in enumerate(Jn_total[:,2]):
                    if jtot == j:
                        ls.append(Jn_total[i,0])
                        ss.append(Jn_total[i,1])
                        
                Jn.append((j,entrance_channels,ls))
            
        if len(J_positive) > 0:
            Jp_total = np.array(J_positive)
            Jp_unique = np.unique(Jp_total[:,2]) 
            
            for j in Jp_unique:
                entrance_channels = np.count_nonzero(Jp_total[:,2] == j)
                
                ls = []; ss = []
                for i, jtot in enumerate(Jp_total[:,2]):
                    if jtot == j:
                        ls.append(Jp_total[i,0])
                        ss.append(Jp_total[i,1])
                    
                Jp.append((j,entrance_channels,ls))

            
            
        if print_out:
            print()
            print('The following arrays describe all possible spin groups for a each parity.\n\
    The data is given as a tuple where the first value is the integer \n\
    or half integer total quantum spin J and the second value is the \n\
    number of entrance channels for that spin group. \n\
    * See the dictionary "possible_Jpi" for a nested packing structure.')
            print()
            print('Spin group data for negative parity\n(J-, #Chs, l-waves)')
            for each in Jn:
                print(each)
            print()
            print('Spin group data for positive parity\n(J+, #Chs, l-waves)')
            for each in Jp:
                print(each)

        # define new attributes for particle_pair object
        self.Jn = Jn
        self.Jp = Jp
        self.J = Jn + Jp

        return




    def sample_all_Jpi(self,  
                        Erange, 
                        Davg, Ggavg, gnavg,
                        save_csv = False, 
                        sammy_run_folder = os.getcwd()):
        """
        Samples a full resonance parameter ladder for each possible spin group.

        This function samples resonance parameters (Energy and widths) for each 
        possible spin group (Jpi) of a given particle pair. The results can be 
        printed to the console and/or saved to a csv. 

        Parameters
        ----------
        self : syndat object
            Particle pair object.
        Erange : array-like
            Array of resolve resonance range energy, only requires min/max.
        Davg : array-like
            Nested list of average level spacing for each spin group number. First 
            list is for negative parity (J-) second is for positive parity (J+).
        Ggavg : array-like
            Nested list of average widths for each spin group number. First 
            list is for negative parity (J-) second is for positive parity (J+).
        gnavg : float
            Nested list of average reduced amplitudes (gn_squared) for each spin group number. First 
            list is for negative parity (J-) second is for positive parity (J+).
        print_out : bool
            User option to print out quantum spin (J) mapping to console.
        save_csv : bool
            User option to save resonance ladders to csv.
        sammy_run_folder : str
            Folder in which the csv(s) containing resparm ladders will be saved.

        Notes
        -----
        Unsure of the average capture width for Gg sampling.
        
        Returns
        -------
        Jn_df : DataFrame
            Pandas DataFrame conatining a resonance parameter ladder for each 
            quantum spin group with negative parity (all J-). The column E gives the energy of the level,
            the column Gn gives the width of the agregate capture channel, and the following columns give
            reduced width amplitudes for particle channels (gn^2), with the headers indicating the waveform (l-wave).
        Jp_df : DataFrame
            Pandas DataFrame conatining a resonance parameter ladder for each 
            quantum spin group with positive parity (all J+). The column E gives the energy of the level,
            the column Gn gives the width of the agregate capture channel, and the following columns give
            reduced width amplitudes for particle channels (gn^2), with the headers indicating the waveform (l-wave).
        """
        
        # ensure enough average parameter values were given
        Jn_avg_length = [len(Davg[0]), len(Ggavg[0]), len(gnavg[0])]
        Jp_avg_length = [len(Davg[1]), len(Ggavg[1]), len(gnavg[1])]
        if any(each != len(self.Jn) for each in Jn_avg_length):
            raise ValueError("Not enough avarage parameters given for negative parity spin groups")
        if any(each != len(self.Jp) for each in Jp_avg_length):
            raise ValueError("Not enough avarage parameters given for positive parity spin groups")
            
    # =============================================================================
    #     negative parity Js
    # =============================================================================
        Jn_ = []
        if len(Davg[0]) > 0:
            for ij, j in enumerate(self.Jn):
                
                # sample resonance levels for each spin group with negative parity
                [levels, level_spacing] = sample_levels.sample_RRR_levels(Erange, Davg[0][ij])
                
                # a single radiative capture width is sampled w/large DOF because of many 'partial' radiative transitions to ground state
                # must divide average by the DOF in order to maintain proper magnitude
                red_gwidth = sample_widths.sample_RRR_widths(levels, Ggavg[0][ij]/100, 100)
                Gwidth = 2*red_gwidth # Gbar = 2*gbar b/c P~1 for gamma channels
                
                # reduced width amplitudes are sampled as single channel (PT or chi with 1 DOF) for each contributing channel then summed
                # while the sum will follow chi square with DOF=#channels, if you just sample the sum over all channels, you ignore
                # differences in the average widths and differences in the penetrability function assosciated with each width
                gnx=[]; gn_lwave = []
                for ichannel, lwave in enumerate(j[2]):      
                    red_nwidth = sample_widths.sample_RRR_widths(levels, gnavg[0][ij], 1)
                    gnx.append(red_nwidth); gn_lwave.append(lwave)
                gn = pd.DataFrame(gnx, index=gn_lwave)
                
                E_Gg = pd.DataFrame([levels, Gwidth], index=['E','Gg'])
                E_Gg_gnx = pd.concat([E_Gg,gn], axis=0)
                E_Gg_Gnx_vert = E_Gg_gnx.transpose()
                
                Jn_.append(E_Gg_Gnx_vert)
                
                if save_csv:
                    E_Gg_Gnx_vert.to_csv(os.path.join(sammy_run_folder, f'Jn_{j[0]}.csv'))
        else:
            print("No average level spacing given for negative parity spin groups")
                
    # =============================================================================
    #       positive parity Js
    # =============================================================================
        Jp_ = []
        if len(Davg[1]) > 0:
            for ij, j in enumerate(self.Jp):
                
                # sample resonance levels for each spin group with negative parity
                [levels, level_spacing] = sample_levels.sample_RRR_levels(Erange, Davg[1][ij])
                
                # a single radiative capture width is sampled w/large DOF because of many 'partial' radiative transitions to ground state
                red_gwidth = sample_widths.sample_RRR_widths(levels, Ggavg[1][ij], 100)
                Gwidth = 2*red_gwidth # Gbar = 2*gbar b/c P~1 for gamma channels
                
                # reduced width amplitudes are sampled as single channel (PT or chi with 1 DOF) for each contributing channel then summed
                # while the sum will follow chi square with DOF=#channels, if you just sample the sum over all channels, you ignore
                # differences in the average widths and differences in the penetrability function assosciated with each width
                gnx=[]; gn_lwave = []
                for ichannel, lwave in enumerate(j[2]):      
                    red_nwidth = sample_widths.sample_RRR_widths(levels, gnavg[1][ij], 1)
                    gnx.append(red_nwidth); gn_lwave.append(lwave)
                gn = pd.DataFrame(gnx, index=gn_lwave)
                
                E_Gg = pd.DataFrame([levels, Gwidth], index=['E','Gg'])
                E_Gg_gnx = pd.concat([E_Gg,gn], axis=0)
                E_Gg_Gnx_vert = E_Gg_gnx.transpose()
                
                Jp_.append(E_Gg_Gnx_vert)
                
                if save_csv:
                    E_Gg_Gnx_vert.to_csv(os.path.join(sammy_run_folder, f'Jp_{j[0]}.csv'))
        else:
            print("No average level spacing given for positive parity spin groups")
                
        
        # =============================================================================
        #       redefine object attributes
        # ============================================================================= 
        self.Jn_resonances = Jn_
        self.Jp_resonances = Jp_

    




    
            
            
            


        
    



