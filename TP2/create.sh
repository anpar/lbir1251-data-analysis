# Run this in git bash with sh create.sh

# Execute notebook to get all outputs
jupyter nbconvert --to notebook --execute TP2.ipynb --inplace

# Convert notebook to WebPDF, remove cells with tag 'correction' and remove tags indicating another version of the assignments
jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'B', 'C', 'D', 'hidden'}" --to webpdf --output "PDF/TP2_consignes_A"
# Convert notebook to another notebook, remove cells with tag 'correction' and remove tags indicating another version of the assignments
jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags="{'correction', 'B', 'C', 'D', 'hidden'}" --to notebook --output "TP2-A.ipynb"

# Repeat for the 3 other versions
jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'C', 'D', 'hidden'}" --to webpdf --output "PDF/TP2_consignes_B"
jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'C', 'D', 'hidden'}" --to notebook --output "TP2-B.ipynb"

jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'B', 'D', 'hidden'}" --to webpdf --output "PDF/TP2_consignes_C"
jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'B', 'D', 'hidden'}" --to notebook --output "TP2-C.ipynb"

jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'B', 'C', 'hidden'}" --to webpdf --output "PDF/TP2_consignes_D"
jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.enabled=True --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'B', 'C', 'hidden'}" --to notebook --output "TP2-D.ipynb"

# Convert full notebook (i.e., with correction and outputs)
jupyter nbconvert TP2.ipynb --to webpdf --output "PDF/TP2_corrections"

# Clear outputs of notebooks
jupyter nbconvert --to notebook --inplace --clear-output *.ipynb