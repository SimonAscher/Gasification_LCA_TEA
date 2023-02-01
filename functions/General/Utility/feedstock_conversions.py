from config import settings


def ultimate_comp_daf_to_wb(C=settings.user_inputs["carbon content"], H=settings.user_inputs["hydrogen content"],
                            N=settings.user_inputs["nitrogen content"], S=settings.user_inputs["sulphur content"],
                            O=settings.user_inputs["oxygen content"], moisture=settings.user_inputs["desired moisture"],
                            ash=settings.user_inputs["ash content"]):
    """
    Converts ultimate composition of a material from % daf (dry ash free)basis to % wb (wet basis).
    By default, takes feedstock data given by user.

    """

    sum_percentages = C + H + N + S + O + moisture + ash
    C_scaled = C * (100 / sum_percentages)
    H_scaled = H * (100 / sum_percentages)
    N_scaled = N * (100 / sum_percentages)
    S_scaled = S * (100 / sum_percentages)
    O_scaled = O * (100 / sum_percentages)

    return {"C": C_scaled, "H": H_scaled, "N": N_scaled, "S": S_scaled, "O": O_scaled, "units": "% wb"}
