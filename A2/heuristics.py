'''
This file will contain different variable ordering heuristics to be used within
bt_search.

1. ord_dh(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the DH heuristic.
2. ord_mrv(csp)
    - Takes in a CSP object (csp).
    - Returns the next Variable to be assigned as per the MRV heuristic.
3. val_lcv(csp, var)
    - Takes in a CSP object (csp), and a Variable object (var)
    - Returns a list of all of var's potential values, ordered from best value 
      choice to worst value choice according to the LCV heuristic.

The heuristics can use the csp argument (CSP object) to get access to the 
variables and constraints of the problem. The assigned variables and values can 
be accessed via methods.
'''

import random
from copy import deepcopy
from propagators import prop_FC


def ord_dh(csp):
    # Get all unassigned variables.
    unasgn_vars = csp.get_all_unasgn_vars()

    # Find the degree of each unassigned variable.
    degrees = [len(csp.get_cons_with_var(var)) for var in unasgn_vars]

    # Find the variable that is involved in the largest number of constraints on other unassigned variables.
    return unasgn_vars[degrees.index(max(degrees))]


def ord_mrv(csp):
    unasgn_vars = csp.get_all_unasgn_vars()

    # Update returned_var, min_num, if we find a variable with a smaller size of domain.
    returned_var = unasgn_vars[0]
    min_num = unasgn_vars[0].cur_domain_size()

    for var in unasgn_vars:

        # If a variable has only one value left, that value is forced,
        # then we should propagate its consequences immediately.
        if var.cur_domain_size() == 1:
            return var

        # Else, updating and keep searching.
        elif var.cur_domain_size() < min_num:
                returned_var = var
                min_num = var.cur_domain_size()

    return returned_var


def val_lcv(csp, var):
    # The keys of this dict are the numbers of prunes,
    # the values of this dict are the values.
    dict_lcv = {}
    lst_lcv = []

    # Check each value in var's domain.
    for val in var.cur_domain():

        # Make a copy of csp, so we don't worry about changing anything in the original csp.
        csp_copy = deepcopy(csp)

        # Find the copy of var.
        for v in csp_copy.get_all_vars():

            if v.name == var.name:
                var_copy = v

        # Assign val for var_copy. Also, we don't need to unassign this var, since it is a copy.
        var_copy.assign(val)
        # Pruning.
        no_deadend, lst_pruned = prop_FC(csp_copy, newVar=var_copy)

        if len(lst_pruned) in dict_lcv:
            dict_lcv[len(lst_pruned)].append(val)
        else:
            dict_lcv[len(lst_pruned)] = [val]

    # Get all numbers of all prunes, ordered from less prunes to more prunes.
    num_prunes = sorted(dict_lcv.keys())

    # Move val from dict_lcv to lst_lcv, ordered from best value choice to worst value choice according to the
    # LCV heuristic.
    # Less prunes = more values left.
    for num in num_prunes:

        lst_lcv.extend([v for v in dict_lcv[num]])

    return lst_lcv
