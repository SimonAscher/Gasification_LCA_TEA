import io
import zipfile

from matplotlib import pyplot as plt

from functions.MonteCarloSimulation import run_simulation

results = run_simulation()

# # Plot results
results_file = results.save_report(storage_path=r"C:\Users\2270577A\OneDrive - University of Glasgow\Desktop\LCA_report",
                                   save_figures=True)
#
# figures_dict = results.figures
# file_type = None
#
# if file_type is None:
#     file_type = ".png"
# zip_file_name = "export.zip"
#
# print(f"Creating archive: {zip_file_name}")
# with zipfile.ZipFile(zip_file_name, mode="w") as zf:
#     for item in results.figures.items():
#         file_name = item[0] + file_type
#         figure = item[1]
#         buf = io.BytesIO()
#         figure.savefig(buf)
#         plt.close()
#         print(f"Writing image {file_name} in the archive")
#         zf.writestr(file_name, buf.getvalue())
#     # zf.extractall(path=r"C:\Users\2270577A\OneDrive - University of Glasgow\Desktop\LCA_report")

# def save_zip(figures_dict, file_type=None):
#     if file_type is None:
#         file_type = ".png"
#     zip_file_name = "export.zip"
#
#     print(f"Creating archive: {zip_file_name}")
#     with zipfile.ZipFile(zip_file_name, mode="w") as zf:
#         for item in results.figures.items():
#             file_name = item[0] + file_type
#             figure = item[1]
#             buf = io.BytesIO()
#             figure.savefig(buf)
#             plt.close()
#             print(f"Writing image {file_name} in the archive")
#             zf.writestr(file_name, buf.getvalue())


