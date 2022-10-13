from functions.general.utility import update_user_inputs_toml, reset_user_inputs_toml

# See if I can write to toml successfully
update_user_inputs_toml("test variable", 25)
update_user_inputs_toml("name", "Simon")

# %%

# See if reset function works
reset_user_inputs_toml()
