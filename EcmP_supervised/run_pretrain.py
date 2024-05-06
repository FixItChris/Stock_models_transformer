#!/usr/bin/python3.9

import argparse
import os
import torch
from exp.exp_pretrain import Exp_Pretrain
import random
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pretraining for PCIE encoder')

    #utility
    parser.add_argument('--result_log_path', type=str, default='./result_log/result_spec1.txt')
    parser.add_argument('--save_results', type=int, default=0, help='save prediction results')

    # random seed
    parser.add_argument('--random_seed', type=int, default=2021, help='random seed')

    # basic config
    parser.add_argument('--is_pretrain', type=int, required=True, default=1, help='status')
    parser.add_argument('--model_id', type=str, default='test', help='model id')#required for training
    parser.add_argument('--model', type=str, required=True, default='PatchTST',
                        help='model name, options: [Autoformer, Informer, Transformer, PatchTST]')

    # data loader
    parser.add_argument('--data', type=str, required=True, default='stock_custom', help='dataset type, try stock_custom for stock data')
    parser.add_argument('--root_path', type=str, default='./stock_data/', help='root path of the data file')
    parser.add_argument('--data_path', type=str, default='None', help='data file, dont modify')
    parser.add_argument('--features', type=str, default='MS',
                        help='forecasting task, options:[M, S, MS]; M:multivariate predict multivariate, S:univariate predict univariate, MS:multivariate predict univariate')
    parser.add_argument('--target', type=str, default='OT', help='target feature in S or MS task')
    parser.add_argument('--freq', type=str, default='d',
                        help='freq for time features encoding, options:[s:secondly, t:minutely, h:hourly, d:daily, b:business days, w:weekly, m:monthly], you can also use more detailed freq like 15min or 3h')
    parser.add_argument('--checkpoints', type=str, default='./pretrain_cp/', help='location of model checkpoints')
    parser.add_argument('--scale', type=int, default=1, help='if use z-score scaler for dataset using std and mean of training set, 1 is true, 0 is false')
    parser.add_argument('--dt_format_str', type=int, default=0, help='the format string for pandas datetime, 0 means use default')

    #prediction  
    parser.add_argument('--prev_scaler', type=str, default='None', help='scaler path for prev_scaler')
    parser.add_argument('--pred_model_load_path', type=str, default='None', help='Path for the model used for prediction')

    # forecasting task
    parser.add_argument('--seq_len', type=int, default=96, help='input sequence length')
    parser.add_argument('--label_len', type=int, default=25, help='start token length, think about this like the lead time(overlap) time between x(input) and y(label)')
    parser.add_argument('--pred_len', type=int, default=96, help='prediction sequence length')


    # DLinear
    #parser.add_argument('--individual', action='store_true', default=False, help='DLinear: a linear layer for each variate(channel) individually')

    # PatchTST
    parser.add_argument('--fc_dropout', type=float, default=0.05, help='fully connected dropout')
    parser.add_argument('--head_dropout', type=float, default=0.0, help='head dropout')
    parser.add_argument('--patch_len', type=int, default=16, help='patch length')
    parser.add_argument('--stride', type=int, default=8, help='stride')
    parser.add_argument('--padding_patch', default='end', help='None: None; end: padding on the end')
    parser.add_argument('--affine', type=int, default=0, help='RevIN-affine; True 1 False 0')
    parser.add_argument('--subtract_last', type=int, default=0, help='0: subtract mean; 1: subtract last')
    parser.add_argument('--decomposition', type=int, default=0, help='decomposition; True 1 False 0')
    parser.add_argument('--kernel_size', type=int, default=25, help='decomposition-kernel')
    parser.add_argument('--individual', type=int, default=0, help='individual head; True 1 False 0')

    #PCIE
    parser.add_argument('--flat_type', type=str, default='linear', help='mlp, linear, for flatten head')
    parser.add_argument('--revin', type=int, default=1, help='RevIN; True 1 False 0')
    parser.add_argument('--d_patch', type=int, default=64, help='The dim size of the pathcing for each channel before mixing')
    parser.add_argument('--first_stage_patching', type=str, default='LOlinears', help='individual channel patching:  linear, LOlinears')
    parser.add_argument('--second_stage_patching', type=str, default='None', help='channel mixing : mlp, linear, and None(flatten the layer into d_model)')
    parser.add_argument('--pe', type=str, default='zeros', help='positional encoding, options : zero, zeros, normal, uniform, sincos')
    parser.add_argument('--learn_pe', type=bool, default=True, help='learnable positional encoding')
    #EcmP_mk2
    parser.add_argument('--dcomp_individual', type=int, default=0, help='use individual Decomp layer for each channel') 

    # Formers 
    parser.add_argument('--embed_type', type=int, default=0, help='0: default 1: value embedding + temporal embedding + positional embedding 2: value embedding + temporal embedding 3: value embedding + positional embedding 4: value embedding')
    parser.add_argument('--enc_in', type=int, default=7, help='encoder input size') # DLinear with --individual, use this hyperparameter as the number of channels
    parser.add_argument('--dec_in', type=int, default=7, help='decoder input size')
    parser.add_argument('--c_out', type=int, default=7, help='output size')
    parser.add_argument('--d_model', type=int, default=512, help='dimension of model')
    parser.add_argument('--n_heads', type=int, default=8, help='num of heads')
    parser.add_argument('--e_layers', type=int, default=2, help='num of encoder layers')
    parser.add_argument('--d_layers', type=int, default=1, help='num of decoder layers')
    parser.add_argument('--d_ff', type=int, default=2048, help='dimension of fcn')
    parser.add_argument('--moving_avg', type=int, default=25, help='window size of moving average')
    parser.add_argument('--factor', type=int, default=1, help='attn factor')

    parser.add_argument('--dropout', type=float, default=0.05, help='dropout')
    parser.add_argument('--embed', type=str, default='timeF',
                        help='time features encoding, options:[timeF, fixed, learned]')
    parser.add_argument('--activation', type=str, default='gelu', help='activation')
    parser.add_argument('--output_attention', action='store_true', help='whether to output attention in ecoder')
    parser.add_argument('--do_predict', type=bool, default=False, help='whether to predict unseen future data')

    # optimization
    parser.add_argument('--num_workers', type=int, default=10, help='data loader num workers')
    parser.add_argument('--itr', type=int, default=2, help='experiments times')
    parser.add_argument('--train_epochs', type=int, default=100, help='train epochs')
    parser.add_argument('--batch_size', type=int, default=128, help='batch size of train input data')
    parser.add_argument('--patience', type=int, default=100, help='early stopping patience')
    parser.add_argument('--learning_rate', type=float, default=0.0001, help='optimizer learning rate')
    parser.add_argument('--des', type=str, default='test', help='exp description')
    parser.add_argument('--loss', type=str, default='mse', help='loss function')
    parser.add_argument('--lradj', type=str, default='type3', help='adjust learning rate')
    parser.add_argument('--pct_start', type=float, default=0.3, help='pct_start')
    parser.add_argument('--use_amp', action='store_true', help='use automatic mixed precision training', default=False)

    # GPU
    parser.add_argument('--use_gpu', type=bool, default=True, help='use gpu')
    parser.add_argument('--gpu', type=int, default=0, help='gpu')
    parser.add_argument('--use_multi_gpu', action='store_true', help='use multiple gpus', default=False)
    parser.add_argument('--devices', type=str, default='0,1,2,3', help='device ids of multile gpus')
    parser.add_argument('--test_flop', action='store_true', default=False, help='See utils/tools for usage')


    #pretrain
    parser.add_argument('--model_load_path', type=str, default='None', help='None for starting fresh, else specify a path')

    args = parser.parse_args()

    # random seed
    fix_seed = args.random_seed
    random.seed(fix_seed)
    torch.manual_seed(fix_seed)
    np.random.seed(fix_seed)

    args.use_gpu = True if torch.cuda.is_available() and args.use_gpu else False

    if args.use_gpu and args.use_multi_gpu:
        args.dvices = args.devices.replace(' ', '')
        device_ids = args.devices.split(',')
        args.device_ids = [int(id_) for id_ in device_ids]
        args.gpu = args.device_ids[0]

    print('pretraining Args in experiment:')
    print(args)

    Exp = Exp_Pretrain

    if args.is_pretrain:

        setting = '{}_{}_{}_ft{}_sl{}_ll{}_pl{}_dm{}_dp{}_pl{}_nh{}_el{}_dl{}_df{}_fc{}_eb{}_{}_dcomp{}_kn{}_{}_{}_rv{}_{}'.format(
            args.model_id,
            args.model,
            args.data,
            args.features,
            args.seq_len,
            args.label_len,
            args.pred_len,
            args.d_model,
            args.d_patch,
            args.patch_len,
            args.n_heads,
            args.e_layers,
            args.d_layers,
            args.d_ff,
            args.factor,
            args.embed,
            args.des,
            args.decomposition,
            args.kernel_size,
            args.first_stage_patching,
            args.second_stage_patching,
            args.revin,
            args.target
            )
        
        for dataset_n in os.listdir(args.root_path):
            args.data_path = os.path.join(args.root_path, dataset_n)

            pretrain = Exp(args)
            print('>>>>>>>start pre-training on stock : {}>>>>>>>>>>>>>>>>>>>>>>>>>>'.format(dataset_n.split(".")[0]))

            pretrain.train(setting)

            torch.cuda.empty_cache()
