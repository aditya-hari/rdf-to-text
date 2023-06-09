python preprocess.py \
  --train_src '/home2/aditya_hari/gsoc/data/processed/br/train_src.txt' \
  --train_tgt '/home2/aditya_hari/gsoc/data/processed/br/train_ref.txt' \
  --eval_src '/home2/aditya_hari/gsoc/data/processed/br/dev_src.txt' \
  --eval_tgt '/home2/aditya_hari/gsoc/data/processed/br/dev_ref.txt' \
  --test_src '/home2/aditya_hari/gsoc/data/processed/br/dev_src.txt' \
  --model gat --lang br --sentencepiece True \
  --vocab_size 4000 --sentencepiece_model 'bpe'


python train_single.py \
  --train_path 'data/processed_graphs/ga/gat/train' \
  --eval_path 'data/processed_graphs/ga/gat/eval' \
  --test_path 'data/processed_graphs/ga/gat/test' \
  --src_vocab 'vocabs/gat/ga/src_vocab' \
  --tgt_vocab 'vocabs/gat/ga/train_vocab.model' \
  --batch_size 1 --enc_type gat --dec_type transformer --model gat --vocab_size 16000 \
  --emb_dim 16 --hidden_size 16 --filter_size 16 --beam_size 5 --mode 'train' \
  --beam_alpha 0.1 --enc_layers 1 --dec_layers 1 --num_heads 1 --sentencepiece True \
  --steps 10000 --eval_steps 1000 --checkpoint 1000 --alpha 0.2 --dropout 0.2 \
  --reg_scale 0.0 --decay True --decay_steps 5000 --lang ga --debug_mode False \
  --eval '/home2/aditya_hari/gsoc/data/processed/ga/dev_src.txt' --eval_ref '/home2/aditya_hari/gsoc/data/processed/ga/dev_ref.txt'

python train_multiple.py \
  --train_path 'data/processed_graphs/eng/gat/train' \
  --eval_path 'data/processed_graphs/eng/gat/eval' \
  --test_path 'data/processed_graphs/eng/gat/test' \
  --src_vocab 'vocabs/gat/eng/src_vocab' \
  --tgt_vocab 'vocabs/gat/eng/train_vocab.model' \
  --batch_size 1 --enc_type gat --dec_type transformer \
  --model multi --vocab_size 16000 --emb_dim 16 --hidden_size 16 \
  --filter_size 16 --beam_size 5 --sentencepiece_model 'bpe' --beam_alpha 0.1 \
  --enc_layers 1 --dec_layers 1 --num_heads 1 --sentencepiece True --steps 10000 \
  --eval_steps 1000 --checkpoint 1000 --alpha 0.2 --dropout 0.2 --mode 'train' \
  --reg_scale 0.0 --decay True --decay_steps 5000 --lang multi --debug_mode False \
  --eval 'data/processed_data/eng/eval_src' --eval_ref 'data/processed_data/eng/eval_tgt'