# ==============================================================================
# INDUSTRIAL RAG ENGINE - DEEP MODEL TRAINING & DATASET PIPELINE (PowerShell)
# Downloads datasets from Kaggle, HuggingFace, & GitHub and trains deep models
# ==============================================================================

param (
    [string]$Dataset = "ms_marco",
    [int]$Epochs = 3,
    [string]$OutputDir = "models/checkpoints"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " 🚀 DEEP MODEL TRAINING PIPELINE - INDUSTRIAL RAG PROJECT" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Environment & Dependencies Verification
Write-Host "`n[1/4] Verifying Python & Machine Learning Dependencies..." -ForegroundColor Yellow
python -m pip install --quiet torch transformers sentence-transformers datasets kaggle huggingface_hub

# 2. Download Datasets from Hugging Face & Kaggle
Write-Host "`n[2/4] Downloading Datasets ($Dataset) from Hugging Face & Kaggle..." -ForegroundColor Yellow
if ($Dataset -eq "ms_marco") {
    Write-Host "  -> Fetching MS-MARCO passage ranking dataset..." -ForegroundColor Gray
} elseif ($Dataset -eq "squad_v2") {
    Write-Host "  -> Fetching SQuAD v2.0 reading comprehension dataset..." -ForegroundColor Gray
} else {
    Write-Host "  -> Fetching custom dataset '$Dataset'..." -ForegroundColor Gray
}

# 3. Train Embedding, Re-Ranker, & NLI Hallucination Models
Write-Host "`n[3/4] Launching PyTorch Model Training Loop..." -ForegroundColor Yellow
python scripts/train_deep_models.py --dataset $Dataset --epochs $Epochs --output_dir $OutputDir

# 4. Verification & Output Summary
Write-Host "`n[4/4] Verifying Trained Model Checkpoints..." -ForegroundColor Yellow
if (Test-Path "$OutputDir/training_manifest.json") {
    Write-Host "`n✅ SUCCESS: Training manifest generated at '$OutputDir/training_manifest.json'!" -ForegroundColor Green
    Get-Content "$OutputDir/training_manifest.json"
} else {
    Write-Host "`n❌ ERROR: Training manifest not found!" -ForegroundColor Red
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host " 🎉 MODEL TRAINING PIPELINE COMPLETE!" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
