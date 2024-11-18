if [ ! -d "./logs" ]; then
    mkdir ./logs
fi


if [ ! -d "./logs/PCIE" ]; then
    mkdir ./logs/PCIE
fi

if [ ! -d "./logs/PCIE/pretrain" ]; then
    mkdir ./logs/PCIE/pretrain
fi

model_name=EcmP_mk3

#patching setting
first_stage_patching=LOlinears
second_stage_patching=None
label_len=0 #reminder the label length is different to the predicted length, lead time(overlap) time between x(input) and y(label)

#decomposition
decomposition=0
kernel_size=9


root_path_name=./data/EcmP_stock_L_2016_24_mix/
data_name=stock_custom_pretrain_v2


# Remove trailing slash if present
last_folder_name="${root_path_name%/}"
# Extract the last folder name
last_folder_name="${last_folder_name##*/}"



random_seed=2023

dt_format_str=0

target=close_pct_change

scale=1
result_log_path=./result_log/PCIE/pretrain/2016_pct.txt

for pred_len in 10 20 40 60
do
    seq_len=60
    python -u EcmP_supervised/run_pretrain_v2.py \
    --model_load_path None \
    --result_log_path $result_log_path \
    --is_pretrain 1\
    --pe zeros\
    --learn_pe True\
    --decomposition $decomposition\
    --kernel_size $kernel_size\
    --first_stage_patching $first_stage_patching\
    --second_stage_patching $second_stage_patching\
    --random_seed $random_seed \
    --root_path $root_path_name \
    --model_id 'PT2016V2PCIE_'$seq_len'_'$pred_len \
    --model $model_name \
    --data $data_name \
    --features MS \
    --seq_len $seq_len \
    --label_len $label_len \
    --pred_len $pred_len \
    --scale $scale\
    --target $target\
    --dt_format_str $dt_format_str\
    --enc_in 9 \
    --e_layers 3 \
    --n_heads 3 \
    --d_patch 0 \
    --d_model 108 \
    --d_ff 256 \
    --dropout 0\
    --fc_dropout 0\
    --head_dropout 0\
    --patch_len 5\
    --stride 1\
    --des 'Exp' \
    --train_epochs 50\
    --lradj 'TST'\
    --pct_start 0.1\
    --itr 1 --batch_size 16 --learning_rate 0.0001 >logs/PCIE/pretrain/$model_name'_'$last_folder_name'_'$model_id_name'_'$seq_len'_'$pred_len.log 
done