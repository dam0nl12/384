'''
All models need to return a CSP object, and a list of lists of Variable objects 
representing the board. The returned list of lists is used to access the 
solution. 

For example, after these three lines of code

    csp, var_array = kenken_csp_model(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the KenKen puzzle.

The grid-only models do not need to encode the cage constraints.

1. binary_ne_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only 
      binary not-equal constraints for both the row and column constraints.

2. nary_ad_grid (worth 10/100 marks)
    - A model of a KenKen grid (without cage constraints) built using only n-ary 
      all-different constraints for both the row and column constraints. 

3. kenken_csp_model (worth 20/100 marks) 
    - A model built using your choice of (1) binary binary not-equal, or (2) 
      n-ary all-different constraints for the grid.
    - Together with KenKen cage constraints.

'''

from cspbase import *
import itertools


# All helper functions are designed for kenken_csp_model(kenken_grid).

# In case that the first element in the kenken_grid is not the size, which can also be a cell-index or operation or
# target-value.
def find_grid_size(kenken_grid):

    for lst in kenken_grid:

        if len(lst) == 1:

            return lst[0]


def create_vars_and_array(grid_size, domain):
    # The collections of all variables. List of variables.
    all_vars = []
    # The collection of variables representing the grid. List of lists(rows) of variables.
    var_array = []

    for r in range(grid_size):

        cur_row = []

        for c in range(grid_size):

            # Name "K" is shorted for "Kenken-Cell."
            var = Variable("K{}{}".format(r, c), domain)

            all_vars.append(var)
            cur_row.append(var)

        var_array.append(cur_row)

    return all_vars, var_array


def convert_cell_index(human_read_index):
    row_index = human_read_index // 10 - 1
    col_index = human_read_index % 10 - 1

    return row_index, col_index


# These four check-functions are basically copied form test.py.
def add_check(lst_vals, target_val):
    return sum(list(lst_vals)) == target_val


def mult_check(lst_vals, target_val):
    prod = 1

    for v in lst_vals:

        prod *= v

    return prod == target_val


def sub_check(lst_vals, target_val):
    # We have to check all permutations! Otherwise, we will have "CSP detected contradiction at root" error.
    # For example, suppose there is a cage: 4 - 1 = 3. Then (4, 1) and (1, 4) are both satisfied tuples.
    # If we don't check both of them, then only (4, 1) might be added into the corresponding constraint.
    for perm in itertools.permutations(lst_vals):

        result = perm[0]
        i = 1

        while i < len(lst_vals):

            result -= perm[i]
            i += 1

        if result == target_val:
            return True

    return False


def div_check(lst_vals, target_val):
    for perm in itertools.permutations(lst_vals):

        result = perm[0]
        i = 1

        while i < len(lst_vals):

            # Use //, not / based on the Piazza post.
            result //= perm[i]
            i += 1

        if result == target_val:
            return True

    return False


# This function should be similar to nQueens(n) in tests.py.
def binary_ne_grid(kenken_grid):
    grid_size = find_grid_size(kenken_grid)
    # Domain is decided by the grid size.
    dom = [i + 1 for i in range(grid_size)]

    all_vars, var_array = create_vars_and_array(grid_size, dom)

    # The collections of all constraints.
    cons = []
    # A row/column cannot have two same values, so function permutations can generate all possible tuples of values.
    # The satisfied tuples are the same for all cells at first.
    sat_tuples = list(itertools.permutations(dom, 2))

    for i in range(grid_size):

        for j in range(grid_size):

            for k in range(j + 1, grid_size):

                # Constraint of a cell and another cell in the same row.
                con_row = Constraint("C(K{}{}, K{}{})".format(i, j, i, k), [var_array[i][j], var_array[i][k]])
                con_row.add_satisfying_tuples(sat_tuples)
                cons.append(con_row)

                # Constraint of a cell and another cell in the same column.
                con_col = Constraint("C(K{}{}, K{}{})".format(j, i, k, i), [var_array[j][i], var_array[k][i]])
                con_col.add_satisfying_tuples(sat_tuples)
                cons.append(con_col)

    # Create CSP and add all cons into it.
    csp = CSP("{}-Kenken".format(grid_size), all_vars)

    for con in cons:

        csp.add_constraint(con)

    return csp, var_array


# This function should also be similar to nQueens(n) in tests.py.
def nary_ad_grid(kenken_grid):
    grid_size = find_grid_size(kenken_grid)
    dom = [i + 1 for i in range(grid_size)]

    all_vars, var_array = create_vars_and_array(grid_size, dom)

    cons = []
    # grid_size * (grid_size - 1) * ... * 2 * * 1 = number of all permutations.
    sat_tuples = list(itertools.permutations(dom, grid_size))

    for i in range(grid_size):

        row_vars = []
        col_vars = []

        for j in range(grid_size):

            row_vars.append(var_array[i][j])
            col_vars.append(var_array[j][i])

        # Constraint of all cells in a row.
        con_row = Constraint("C(Row{})".format(i), row_vars)
        con_row.add_satisfying_tuples(sat_tuples)
        cons.append(con_row)

        # Constraint of all cells in a column.
        con_col = Constraint("C(Col{})".format(i), col_vars)
        con_col.add_satisfying_tuples(sat_tuples)
        cons.append(con_col)

    # Create CSP and add all cons into it.
    csp = CSP("{}-Kenken".format(grid_size), all_vars)

    for con in cons:

        csp.add_constraint(con)

    return csp, var_array


def kenken_csp_model(kenken_grid):
    # Use binary_ne_grid(kenken_grid) to build the complete model, it is much faster than nary_ad_grid(kenken_grid).
    # var_array is still the same, but more constraints need to be added into csp.
    csp, var_array = binary_ne_grid(kenken_grid)

    grid_size = find_grid_size(kenken_grid)
    dom = [i + 1 for i in range(grid_size)]

    cage_count = 0
    cons = []

    # Generate all cage-constraints.
    for cage in kenken_grid:

        # A forced value for a cell.
        if len(cage) == 2:
            row_index, col_index = convert_cell_index(cage[0])

            forced_value = cage[1]
            sat_tuples = [(forced_value,)]

            con = Constraint("Cage{}".format(cage_count), [var_array[row_index][col_index]])
            con.add_satisfying_tuples(sat_tuples)
            cons.append(con)

            cage_count += 1

        # A cage with at least 2 cells.
        elif len(cage) > 2:
            operation = cage[-1]
            target_value = cage[-2]

            sat_tuples = []
            cage_vars = []

            # Get all variables in this cage.
            for cell in cage[0: len(cage) - 2]:

                row_index, col_index = convert_cell_index(cell)
                cage_vars.append(var_array[row_index][col_index])

            # Get all possible values.
            # Use product, not permutation, because a cage can have the same values.
            for vals in itertools.product(dom, repeat=len(cage) - 2):

                if ((operation == 0 and add_check(vals, target_value))
                        or (operation == 1 and sub_check(vals, target_value))
                        or (operation == 2 and div_check(vals, target_value))
                        or (operation == 3 and mult_check(vals, target_value))):
                    sat_tuples.append(vals)

            con = Constraint("Cage{}".format(cage_count), cage_vars)
            con.add_satisfying_tuples(sat_tuples)
            cons.append(con)

            cage_count += 1

    for con in cons:

        csp.add_constraint(con)

    return csp, var_array
