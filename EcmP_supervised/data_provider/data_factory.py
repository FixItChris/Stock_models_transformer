from data_provider.data_loader import Dataset_ETT_hour, Dataset_ETT_minute, Dataset_Custom, Dataset_Pred
from data_provider.custom_data_loader import Dataset_Custom_stock, Dataset_Custom_stock_pred, Dataset_Custom_stock_pretrain
from data_provider.custom_data_loader_pretrain import Dataset_Custom_stock_pretrain_v2
from torch.utils.data import DataLoader

data_dict = {
    'ETTh1': Dataset_ETT_hour,
    'ETTh2': Dataset_ETT_hour,
    'ETTm1': Dataset_ETT_minute,
    'ETTm2': Dataset_ETT_minute,
    'custom': Dataset_Custom,
    'stock_custom': Dataset_Custom_stock,
    'stock_custom_pred': Dataset_Custom_stock_pred,
    'stock_custom_pretrain': Dataset_Custom_stock_pretrain,
    'stock_custom_pretrain_v2' : Dataset_Custom_stock_pretrain_v2
}


def data_provider(args, flag):
    Data = data_dict[args.data]
    timeenc = 0 if args.embed != 'timeF' else 1

    if flag == 'test':
        shuffle_flag = False
        drop_last = True
        batch_size = args.batch_size
        freq = args.freq
    elif flag == 'pred':
        shuffle_flag = False
        drop_last = False
        batch_size = 1
        freq = args.freq
        if args.data != 'stock_custom_pred':
            Data = Dataset_Pred
    else:
        shuffle_flag = True
        drop_last = True
        batch_size = args.batch_size
        freq = args.freq

    if args.data == 'stock_custom_pred':

        data_set = Data(
            root_path=args.root_path,
            data_path=args.data_path,
            flag=flag,
            size=[args.seq_len, args.label_len, args.pred_len],
            features=args.features,
            target=args.target,
            timeenc=timeenc,
            freq=freq,
            scale=args.scale,        #custom section dont worry about the 
            prev_scaler=args.prev_scaler
        )
        
    elif args.data == 'stock_custom': 
        data_set = Data(
            root_path=args.root_path,
            data_path=args.data_path,
            flag=flag,
            size=[args.seq_len, args.label_len, args.pred_len],
            features=args.features,
            target=args.target,
            timeenc=timeenc,
            freq=freq,
            scale=args.scale,        #custom section dont worry about the 
            dt_format_str=args.dt_format_str
        )
    
    elif args.data == 'stock_custom_pretrain':
        data_set = Data(
            root_path=args.root_path,
            data_path=args.data_path,
            flag=flag,
            size=[args.seq_len, args.label_len, args.pred_len],
            features=args.features,
            target=args.target,
            timeenc=timeenc,
            freq=freq,
            scale=args.scale        
        )
    
    elif args.data == 'stock_custom_pretrain_v2':
        data_set = Data(
            root_path=args.root_path,
            data_folder=args.root_path,
            flag=flag,
            size=[args.seq_len, args.label_len, args.pred_len],
            features=args.features,
            target=args.target,
            timeenc=timeenc,
            freq=freq,
            scale=args.scale     
        )
    
    else: #default

        data_set = Data(
        root_path=args.root_path,
        data_path=args.data_path,
        flag=flag,
        size=[args.seq_len, args.label_len, args.pred_len],
        features=args.features,
        target=args.target,
        timeenc=timeenc,
        freq=freq
        )
        

    print(flag, len(data_set))
    data_loader = DataLoader(
        data_set,
        batch_size=batch_size,
        shuffle=shuffle_flag,
        num_workers=args.num_workers,
        drop_last=drop_last)
    return data_set, data_loader
