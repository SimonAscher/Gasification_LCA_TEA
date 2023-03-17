from configs import triangular_dist_maker, range_dist_maker, fixed_dist_maker
from functions.MonteCarloSimulation import get_distribution_draws
from config import settings

# a = settings.data.economic.electricity_wholesale_prices.most_recent
# b = settings.user_inputs.country
# c = a[b]
# d = settings.data.economic.electricity_wholesale_prices.most_recent[settings.user_inputs.country]

# tri = triangular_dist_maker(1, 1.2, 2)
# output = get_distribution_draws(tri, length_array=1)
# output2 = get_distribution_draws(tri, length_array=1)

#
# import toml
# dictionary = {'section1' : { 'name' : 'abcd' , 'language' : 'python' } , 'section2' : { 'name' : 'aaaa' , 'language' : 'java' } }
#
# toml.dumps(dictionary)
#
#
# absolute_raw_filepath=r"C:\Users\2270577A\PycharmProjects\PhD_LCA_TEA\configs\user_inputs.toml"
#
# data = toml.load(absolute_raw_filepath)
#
# # Update value
# data["default"] = dictionary
#
# # Update toml
# f = open(absolute_raw_filepath, 'w')
# toml.dump(data, f)
# f.close()