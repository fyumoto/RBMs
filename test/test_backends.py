import paysage.backends.python_backend.matrix as py_matrix
import paysage.backends.python_backend.nonlinearity as py_func
import paysage.backends.python_backend.rand as py_rand

import paysage.backends.pytorch_backend.matrix as torch_matrix
import paysage.backends.pytorch_backend.nonlinearity as torch_func
import paysage.backends.pytorch_backend.rand as torch_rand

import pytest

def test_conversion():

    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)
    py_torch_x = torch_matrix.to_numpy_array(torch_x)

    assert py_matrix.allclose(py_x, py_torch_x), \
    "python -> torch -> python failure"

    torch_rand.set_seed()
    torch_y = torch_rand.rand(shape)
    py_y = torch_matrix.to_numpy_array(torch_y)
    torch_py_y = torch_matrix.float_tensor(py_y)

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure"

def test_transpose():

    shape = (100, 100)

    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_x_T = py_matrix.transpose(py_x)
    py_torch_x_T = torch_matrix.to_numpy_array(torch_matrix.transpose(torch_x))

    assert py_matrix.allclose(py_x_T, py_torch_x_T), \
    "python -> torch -> python failure: transpose"

    torch_rand.set_seed()
    torch_y = torch_rand.rand(shape)
    py_y = torch_matrix.to_numpy_array(torch_y)

    torch_y_T = torch_matrix.transpose(torch_y)
    torch_py_y_T = torch_matrix.float_tensor(py_matrix.transpose(py_y))

    assert torch_matrix.allclose(torch_y_T, torch_py_y_T), \
    "torch -> python -> torch failure: transpose"

def test_zeros():

    shape = (100, 100)

    py_zeros = py_matrix.zeros(shape)
    torch_zeros = torch_matrix.zeros(shape)

    torch_py_zeros = torch_matrix.float_tensor(py_zeros)
    py_torch_zeros = torch_matrix.to_numpy_array(torch_zeros)

    assert py_matrix.allclose(py_zeros, py_torch_zeros), \
    "python -> torch -> python failure: zeros"

    assert torch_matrix.allclose(torch_zeros, torch_py_zeros), \
    "torch -> python -> torch failure: zeros"

def test_ones():

    shape = (100, 100)

    py_ones = py_matrix.ones(shape)
    torch_ones = torch_matrix.ones(shape)

    torch_py_ones = torch_matrix.float_tensor(py_ones)
    py_torch_ones = torch_matrix.to_numpy_array(torch_ones)

    assert py_matrix.allclose(py_ones, py_torch_ones), \
    "python -> torch -> python failure: ones"

    assert torch_matrix.allclose(torch_ones, torch_py_ones), \
    "torch -> python -> torch failure: ones"

def test_diag():

    shape = (100,)

    py_vec = py_rand.randn(shape)
    py_mat = py_matrix.diagonal_matrix(py_vec)
    py_diag = py_matrix.diag(py_mat)

    assert py_matrix.allclose(py_vec, py_diag), \
    "python vec -> matrix -> vec failure: diag"

    torch_vec = torch_rand.randn(shape)
    torch_mat = torch_matrix.diagonal_matrix(torch_vec)
    torch_diag = torch_matrix.diag(torch_mat)

    assert torch_matrix.allclose(torch_vec, torch_diag), \
    "torch vec -> matrix -> vec failure: diag"

def test_fill_diagonal():

    n = 10

    py_mat = py_matrix.identity(n)
    torch_mat = torch_matrix.identity(n)

    fill_value = 2.0

    py_mult = fill_value * py_mat
    py_matrix.fill_diagonal(py_mat, fill_value)

    assert py_matrix.allclose(py_mat, py_mult), \
    "python fill != python multiplly for diagonal matrix"

    torch_mult = fill_value * torch_mat
    torch_matrix.fill_diagonal(torch_mat, fill_value)

    assert torch_matrix.allclose(torch_mat, torch_mult), \
    "torch fill != python multiplly for diagonal matrix"

    py_torch_mat = torch_matrix.to_numpy_array(torch_mat)

    assert py_matrix.allclose(py_torch_mat, py_mat), \
    "torch fill != python fill"

def test_sign():

    shape = (100,100)

    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_sign = py_matrix.sign(py_mat)
    torch_sign = torch_matrix.sign(torch_mat)

    py_torch_sign = torch_matrix.to_numpy_array(torch_sign)
    py_py_sign = py_matrix.to_numpy_array(py_sign)

    assert py_matrix.allclose(py_torch_sign, py_py_sign), \
    "python sign != torch sign"

def test_clip():

    shape = (100,100)

    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # test two sided clip
    py_clipped = py_matrix.clip(py_mat, a_min=0, a_max=1)
    torch_clipped = torch_matrix.clip(torch_mat, a_min=0, a_max=1)

    py_torch_clipped = torch_matrix.to_numpy_array(torch_clipped)

    assert py_matrix.allclose(py_clipped, py_torch_clipped), \
    "python clip != torch clip: two sided"

    # test lower clip
    py_clipped = py_matrix.clip(py_mat, a_min=0)
    torch_clipped = torch_matrix.clip(torch_mat, a_min=0)

    py_torch_clipped = torch_matrix.to_numpy_array(torch_clipped)

    assert py_matrix.allclose(py_clipped, py_torch_clipped), \
    "python clip != torch clip: lower"

    # test upper clip
    py_clipped = py_matrix.clip(py_mat, a_max=1)
    torch_clipped = torch_matrix.clip(torch_mat, a_max=1)

    py_torch_clipped = torch_matrix.to_numpy_array(torch_clipped)

    assert py_matrix.allclose(py_clipped, py_torch_clipped), \
    "python clip != torch clip: upper"

def test_clip_inplace():

    shape = (100,100)

    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    # test two sided clip
    py_matrix.clip_inplace(py_mat, a_min=0, a_max=1)
    torch_matrix.clip_inplace(torch_mat, a_min=0, a_max=1)

    py_torch_clipped = torch_matrix.to_numpy_array(torch_mat)

    assert py_matrix.allclose(py_mat, py_torch_clipped), \
    "python clip inplace != torch clip inplace: two sided"

    # test lower clip
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_matrix.clip_inplace(py_mat, a_min=0)
    torch_matrix.clip_inplace(torch_mat, a_min=0)

    py_torch_clipped = torch_matrix.to_numpy_array(torch_mat)

    assert py_matrix.allclose(py_mat, py_torch_clipped), \
    "python clip inplace != torch clip inplace: lower"

    # test upper clip
    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_matrix.clip_inplace(py_mat, a_max=1)
    torch_matrix.clip_inplace(torch_mat, a_max=1)

    py_torch_clipped = torch_matrix.to_numpy_array(torch_mat)

    assert py_matrix.allclose(py_mat, py_torch_clipped), \
    "python clip inplace != torch clip inplace: upper"

def test_tround():

    shape = (100,100)

    py_mat = py_rand.randn(shape)
    torch_mat = torch_matrix.float_tensor(py_mat)

    py_round = py_matrix.tround(py_mat)
    torch_round = torch_matrix.tround(torch_mat)

    py_torch_round = torch_matrix.to_numpy_array(torch_round)
    py_py_round = py_matrix.to_numpy_array(py_round)

    assert py_matrix.allclose(py_torch_round, py_py_round), \
    "python round != torch round"


# ----- Nonlinearities ----- #

def test_tabs():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.tabs(py_x)
    torch_y = torch_func.tabs(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: tabs"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: tabs"

def test_exp():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.exp(py_x)
    torch_y = torch_func.exp(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: exp"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: exp"

def test_log():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.log(py_x)
    torch_y = torch_func.log(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: log"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: log"

def test_tanh():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.tanh(py_x)
    torch_y = torch_func.tanh(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: tanh"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: tanh"

def test_expit():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.expit(py_x)
    torch_y = torch_func.expit(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: expit"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: expit"

def test_reciprocal():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.reciprocal(py_x)
    torch_y = torch_func.reciprocal(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: reciprocal"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: reciprocal"

def test_atanh():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = 2 * py_rand.rand(shape) - 1
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.atanh(py_x)
    torch_y = torch_func.atanh(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    # the atanh function is a bit less precise than the others
    # so the tolerance is a bit more flexible
    assert py_matrix.allclose(py_y, py_torch_y, rtol=1e-05, atol=1e-07), \
    "python -> torch -> python failure: atanh"

    assert torch_matrix.allclose(torch_y, torch_py_y, rtol=1e-05, atol=1e-07), \
    "torch -> python -> torch failure: atanh"

def test_sqrt():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.sqrt(py_x)
    torch_y = torch_func.sqrt(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: sqrt"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: sqrt"

def test_square():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.square(py_x)
    torch_y = torch_func.square(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: square"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: square"

def test_tpow():
    shape = (100, 100)
    power = 3
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.tpow(py_x, power)
    torch_y = torch_func.tpow(torch_x, power)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: tpow"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: tpow"

def test_cosh():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.cosh(py_x)
    torch_y = torch_func.cosh(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: cosh"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: cosh"

def test_logaddexp():
    shape = (100, 100)
    py_rand.set_seed()
    py_x_1 = py_rand.randn(shape)
    py_x_2 = py_rand.randn(shape)

    torch_x_1 = torch_matrix.float_tensor(py_x_1)
    torch_x_2 = torch_matrix.float_tensor(py_x_2)

    py_y = py_func.logaddexp(py_x_1, py_x_2)
    torch_y = torch_func.logaddexp(torch_x_1, torch_x_2)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: cosh"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: cosh"

def test_logcosh():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.logcosh(py_x)
    torch_y = torch_func.logcosh(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: logcosh"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: logcosh"

def test_acosh():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = 1 + py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.acosh(py_x)
    torch_y = torch_func.acosh(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: acosh"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: acosh"

def test_logit():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.rand(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.logit(py_x)
    torch_y = torch_func.logit(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: logit"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: logit"

def test_softplus():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.softplus(py_x)
    torch_y = torch_func.softplus(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: softplus"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: softplus"

def test_cos():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.cos(py_x)
    torch_y = torch_func.cos(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: cos"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: cos"

def test_sin():
    shape = (100, 100)
    py_rand.set_seed()
    py_x = py_rand.randn(shape)
    torch_x = torch_matrix.float_tensor(py_x)

    py_y = py_func.sin(py_x)
    torch_y = torch_func.sin(torch_x)

    torch_py_y = torch_matrix.float_tensor(py_y)
    py_torch_y = torch_matrix.to_numpy_array(torch_y)

    assert py_matrix.allclose(py_y, py_torch_y), \
    "python -> torch -> python failure: sin"

    assert torch_matrix.allclose(torch_y, torch_py_y), \
    "torch -> python -> torch failure: sin"


if __name__ == "__main__":
    test_conversion()
    test_transpose()
    test_zeros()
    test_ones()
    test_diag()
    test_fill_diagonal()
    test_sign()
    test_clip()
    test_clip_inplace()
    test_tround()

    test_tabs()
    test_exp()
    test_log()
    test_tanh()
    test_expit()
    test_reciprocal()
    test_atanh()
    test_sqrt()
    test_square()
    test_tpow()
    test_cosh()
    test_logaddexp()
    test_logcosh()
    test_acosh()
    test_logit()
    test_softplus()
    test_cos()
    test_sin()