# Run this in git bash with sh generate_pdf.sh

# Execute notebook to get all outputs
jupyter nbconvert --to notebook --execute TP2.ipynb --inplace

# Convert notebook to WebPDF, remove cell with tag 'correction' and remove tags indicating another version of the assignments
jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'B', 'C', 'D'}" --to webpdf --output "PDF/TP2_consignes_A"

jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'C', 'D'}" --to webpdf --output "PDF/TP2_consignes_B"

jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'B', 'D'}" --to webpdf --output "PDF/TP2_consignes_C"

jupyter nbconvert TP2.ipynb --TagRemovePreprocessor.remove_cell_tags="{'correction', 'A', 'B', 'C'}" --to webpdf --output "PDF/TP2_consignes_D"

# Convert full notebook (i.e., with correction and outputs)
jupyter nbconvert TP2.ipynb --to webpdf --output "PDF/TP2_corrections"