# Copyright 2020 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Uniform Distribution"""
from mindspore.ops import operations as P
from mindspore.ops import composite as C
from mindspore.common import dtype as mstype
from .distribution import Distribution
from ._utils.utils import convert_to_batch, check_greater, check_type, check_distribution_name,\
                          raise_none_error

class Uniform(Distribution):
    """
    Example class: Uniform Distribution.

    Args:
        low (int, float, list, numpy.ndarray, Tensor, Parameter): lower bound of the distribution.
        high (int, float, list, numpy.ndarray, Tensor, Parameter): upper bound of the distribution.
        seed (int): seed to use in sampling. Default: 0.
        dtype (mindspore.dtype): type of the distribution. Default: mstype.float32.
        name (str): name of the distribution. Default: Uniform.

    Note:
        low should be stricly less than high.
        Dist_spec_args are high and low.

    Examples:
        >>> # To initialize a Uniform distribution of mean 3.0 and standard deviation 4.0
        >>> import mindspore.nn.probability.distribution as msd
        >>> u = msd.Uniform(0.0, 1.0, dtype=mstype.float32)
        >>>
        >>> # The following creates two independent Uniform distributions
        >>> u = msd.Uniform([0.0, 0.0], [1.0, 2.0], dtype=mstype.float32)
        >>>
        >>> # A Uniform distribution can be initilized without arguments
        >>> # In this case, high and low must be passed in through args during function calls.
        >>> u = msd.Uniform(dtype=mstype.float32)
        >>>
        >>> # To use Uniform in a network
        >>> class net(Cell):
        >>>     def __init__(self)
        >>>         super(net, self).__init__():
        >>>         self.u1 = msd.Uniform(0.0, 1.0, dtype=mstype.float32)
        >>>         self.u2 = msd.Uniform(dtype=mstype.float32)
        >>>
        >>>     # All the following calls in construct are valid
        >>>     def construct(self, value, low_b, high_b, low_a, high_a):
        >>>
        >>>         # Similar calls can be made to other probability functions
        >>>         # by replacing 'prob' with the name of the function
        >>>         ans = self.u1.prob(value)
        >>>         # Evaluate with the respect to distribution b
        >>>         ans = self.u1.prob(value, low_b, high_b)
        >>>
        >>>         # High and low must be passed in during function calls
        >>>         ans = self.u2.prob(value, low_a, high_a)
        >>>
        >>>         # Functions 'sd', 'var', 'entropy' have the same usage as 'mean'
        >>>         # Will return 0.5
        >>>         ans = self.u1.mean()
        >>>         # Will return (low_b + high_b) / 2
        >>>         ans = self.u1.mean(low_b, high_b)
        >>>
        >>>         # High and low must be passed in during function calls
        >>>         ans = self.u2.mean(low_a, high_a)
        >>>
        >>>         # Usage of 'kl_loss' and 'cross_entropy' are similar
        >>>         ans = self.u1.kl_loss('Uniform', low_b, high_b)
        >>>         ans = self.u1.kl_loss('Uniform', low_b, high_b, low_a, high_a)
        >>>
        >>>         # Additional high and low must be passed
        >>>         ans = self.u2.kl_loss('Uniform', low_b, high_b, low_a, high_a)
        >>>
        >>>         # Sample
        >>>         ans = self.u1.sample()
        >>>         ans = self.u1.sample((2,3))
        >>>         ans = self.u1.sample((2,3), low_b, high_b)
        >>>         ans = self.u2.sample((2,3), low_a, high_a)
    """

    def __init__(self,
                 low=None,
                 high=None,
                 seed=0,
                 dtype=mstype.float32,
                 name="Uniform"):
        """
        Constructor of Uniform distribution.
        """
        param = dict(locals())
        valid_dtype = mstype.float_type
        check_type(dtype, valid_dtype, "Uniform")
        super(Uniform, self).__init__(seed, dtype, name, param)
        self.parameter_type = dtype
        if low is not None and high is not None:
            self._low = convert_to_batch(low, self.broadcast_shape, dtype)
            self._high = convert_to_batch(high, self.broadcast_shape, dtype)
            check_greater(self.low, self.high, "low value", "high value")
        else:
            self._low = low
            self._high = high

        # ops needed for the class
        self.squeeze = P.Squeeze(0)
        self.cast = P.Cast()
        self.const = P.ScalarToArray()
        self.dtypeop = P.DType()
        self.exp = P.Exp()
        self.fill = P.Fill()
        self.less = P.Less()
        self.lessequal = P.LessEqual()
        self.log = P.Log()
        self.logicaland = P.LogicalAnd()
        self.select = P.Select()
        self.shape = P.Shape()
        self.sq = P.Square()
        self.sqrt = P.Sqrt()
        self.zeroslike = P.ZerosLike()
        self.uniform = C.uniform

    def extend_repr(self):
        if self.is_scalar_batch:
            str_info = f'low = {self.low}, high = {self.high}'
        else:
            str_info = f'batch_shape = {self._broadcast_shape}'
        return str_info

    @property
    def low(self):
        """
        Return lower bound of the distribution.
        """
        return self._low

    @property
    def high(self):
        """
        Return upper bound of the distribution.
        """
        return self._high

    def _range(self, low=None, high=None):
        r"""
        Return the range of the distribution.
        .. math::
            range(U) = high -low
        """
        low = self.cast(low, self.parameter_type) if low is not None else self.low
        if low is None:
            raise_none_error("low")
        high = self.cast(high, self.parameter_type) if high is not None else self.high
        if high is None:
            raise_none_error("high")
        return high - low

    def _mean(self, low=None, high=None):
        r"""
        .. math::
            MEAN(U) = \frac{low + high}{2}.
        """
        low = self.cast(low, self.parameter_type) if low is not None else self.low
        if low is None:
            raise_none_error("low")
        high = self.cast(high, self.parameter_type) if high is not None else self.high
        if high is None:
            raise_none_error("high")
        return (low + high) / 2.

    def _var(self, low=None, high=None):
        r"""
        .. math::
            VAR(U) = \frac{(high -low) ^ 2}{12}.
        """
        low = self.cast(low, self.parameter_type) if low is not None else self.low
        if low is None:
            raise_none_error("low")
        high = self.cast(high, self.parameter_type) if high is not None else self.high
        if high is None:
            raise_none_error("high")
        return self.sq(high - low) / 12.0

    def _entropy(self, low=None, high=None):
        r"""
        .. math::
            H(U) = \log(high - low).
        """
        low = self.cast(low, self.parameter_type) if low is not None else self.low
        if low is None:
            raise_none_error("low")
        high = self.cast(high, self.parameter_type) if high is not None else self.high
        if high is None:
            raise_none_error("high")
        return self.log(high - low)

    def _cross_entropy(self, dist, low_b, high_b, low_a=None, high_a=None):
        """
        Evaluate cross_entropy between Uniform distributoins.

        Args:
            dist (str): type of the distributions. Should be "Uniform" in this case.
            low_b (Tensor): lower bound of distribution b.
            high_b (Tensor): upper bound of distribution b.
            low_a (Tensor): lower bound of distribution a. Default: self.low.
            high_a (Tensor): upper bound of distribution a. Default: self.high.
        """
        check_distribution_name(dist, 'Uniform')
        return self._entropy(low=low_a, high=high_a) + self._kl_loss(dist, low_b, high_b, low_a, high_a)

    def _prob(self, value, low=None, high=None):
        r"""
        pdf of Uniform distribution.

        Args:
            value (Tensor): value to be evaluated.
            low (Tensor): lower bound of the distribution. Default: self.low.
            high (Tensor): upper bound of the distribution. Default: self.high.

        .. math::
            pdf(x) = 0 if x < low;
            pdf(x) = \frac{1.0}{high -low} if low <= x <= high;
            pdf(x) = 0 if x > high;
        """
        if value is None:
            raise_none_error("value")
        value = self.cast(value, self.dtype)
        low = self.cast(low, self.parameter_type) if low is not None else self.low
        if low is None:
            raise_none_error("low")
        high = self.cast(high, self.parameter_type) if high is not None else self.high
        if high is None:
            raise_none_error("high")
        neg_ones = self.fill(self.dtype, self.shape(value), -1.0)
        prob = self.exp(neg_ones * self.log(high - low))
        broadcast_shape = self.shape(prob)
        zeros = self.fill(self.dtypeop(prob), broadcast_shape, 0.0)
        comp_lo = self.less(value, low)
        comp_hi = self.lessequal(value, high)
        less_than_low = self.select(comp_lo, zeros, prob)
        return self.select(comp_hi, less_than_low, zeros)

    def _kl_loss(self, dist, low_b, high_b, low_a=None, high_a=None):
        """
        Evaluate uniform-uniform kl divergence, i.e. KL(a||b).

        Args:
            dist (str): type of the distributions. Should be "Uniform" in this case.
            low_b (Tensor): lower bound of distribution b.
            high_b (Tensor): upper bound of distribution b.
            low_a (Tensor): lower bound of distribution a. Default: self.low.
            high_a (Tensor): upper bound of distribution a. Default: self.high.
        """
        check_distribution_name(dist, 'Uniform')
        if low_b is None:
            raise_none_error("low_b")
        if high_b is None:
            raise_none_error("high_b")
        low_b = self.cast(low_b, self.parameter_type)
        high_b = self.cast(high_b, self.parameter_type)
        low_a = self.cast(low_a, self.parameter_type) if low_a is not None else self.low
        if low_a is None:
            raise_none_error("low_a")
        high_a = self.cast(high_a, self.parameter_type) if high_a is not None else self.high
        if high_a is None:
            raise_none_error("high_a")
        kl = self.log(high_b - low_b) / self.log(high_a - low_a)
        comp = self.logicaland(self.lessequal(low_b, low_a), self.lessequal(high_a, high_b))
        return self.select(comp, kl, self.log(self.zeroslike(kl)))

    def _cdf(self, value, low=None, high=None):
        r"""
        cdf of Uniform distribution.

        Args:
            value (Tensor): value to be evaluated.
            low (Tensor): lower bound of the distribution. Default: self.low.
            high (Tensor): upper bound of the distribution. Default: self.high.

        .. math::
            cdf(x) = 0 if x < low;
            cdf(x) = \frac{x - low}{high -low} if low <= x <= high;
            cdf(x) = 1 if x > high;
        """
        if value is None:
            raise_none_error("value")
        value = self.cast(value, self.dtype)
        low = self.cast(low, self.parameter_type) if low is not None else self.low
        if low is None:
            raise_none_error("low")
        high = self.cast(high, self.parameter_type) if high is not None else self.high
        if high is None:
            raise_none_error("high")
        prob = (value - low) / (high - low)
        broadcast_shape = self.shape(prob)
        zeros = self.fill(self.dtypeop(prob), broadcast_shape, 0.0)
        ones = self.fill(self.dtypeop(prob), broadcast_shape, 1.0)
        comp_lo = self.less(value, low)
        comp_hi = self.less(value, high)
        less_than_low = self.select(comp_lo, zeros, prob)
        return self.select(comp_hi, less_than_low, ones)

    def _sample(self, shape=(), low=None, high=None):
        """
        Sampling.

        Args:
            shape (tuple): shape of the sample. Default: ().
            low (Tensor): lower bound of the distribution. Default: self.low.
            high (Tensor): upper bound of the distribution. Default: self.high.

        Returns:
            Tensor, shape is shape + batch_shape.
        """
        low = self.cast(low, self.parameter_type) if low is not None else self.low
        if low is None:
            raise_none_error("low")
        high = self.cast(high, self.parameter_type) if high is not None else self.high
        if high is None:
            raise_none_error("high")
        broadcast_shape = self.shape(low + high)
        origin_shape = shape + broadcast_shape
        if origin_shape == ():
            sample_shape = (1,)
        else:
            sample_shape = origin_shape
        l_zero = self.const(0.0)
        h_one = self.const(1.0)
        sample_uniform = self.uniform(sample_shape, l_zero, h_one, self.seed)
        sample = (high - low) * sample_uniform + low
        value = self.cast(sample, self.dtype)
        if origin_shape == ():
            value = self.squeeze(value)
        return value
