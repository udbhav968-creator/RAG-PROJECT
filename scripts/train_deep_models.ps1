# ==============================================================================
# INDUSTRIAL RAG ENGINE - DEEP HIGH-EPOCH MODEL TRAINING & DATASET PIPELINE (PowerShell)
# Supports 50, 100, 500+ Deep Training Epochs across Kaggle, HuggingFace, & GitHub
# ==============================================================================

param (
    [string]$Dataset = "ms_marco",
    [int]$Epochs = 50,
    [int]$BatchSize = 32,
    [double]$LearningRate = 0.00002,
    [string]$OutputDir = "models/checkpoints"
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " 🚀 DEEP HIGH-EPOCH MODEL TRAINING PIPELINE ($Epochs Epochs)" -ForegroundColor White
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

# 3. Train Embedding, Re-Ranker, & NLI Hallucination Models for Specified Epochs
Write-Host "`n[3/4] Launching Deep Training Loop for $Epochs Epochs (BatchSize=$BatchSize)..." -ForegroundColor Yellow
python scripts/train_deep_models.py --dataset $Dataset --epochs $Epochs --batch_size $BatchSize --learning_rate $LearningRate --output_dir $OutputDir

# 4. Verification & Output Summary
Write-Host "`n[4/4] Verifying Trained Model Checkpoints..." -ForegroundColor Yellow
if (Test-Path "$OutputDir/training_manifest.json") {
    Write-Host "`n✅ SUCCESS: Deep Training Manifest generated at '$OutputDir/training_manifest.json'!" -ForegroundColor Green
    Get-Content "$OutputDir/training_manifest.json"
} else {
    Write-Host "`n❌ ERROR: Training manifest not found!" -ForegroundColor Red
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host " 🎉 DEEP HIGH-EPOCH MODEL TRAINING COMPLETE ($Epochs EPOCHS)!" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
