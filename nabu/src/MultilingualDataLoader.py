from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os

import sentencepiece as spm
import tensorflow as tf

from src.utils.PreprocessingUtils import PreProcess
from src.utils.model_utils import PreProcessSentence, _tensorize, Padding as padding
from src.utils.model_utils import PreprocessSeqSource

languages = ['br', 'cy', 'ga', 'mt', 'ru']


def LoadMultlingualDataset(args):
  """
  Function to load individual datasets and Preprocess them
   individuall. A language token in also added at
  the start of each dataset.
  Takes in Preprocessed data and trains a sentencepiece model on the
  target sentences if enables, else uses default tensorflow tokenizer.

  :param args: The args obj which contains paths to the preprocessed files
  :type args: ArgParse object
  :return: The mulitlingual dataset, source and target vocab
  :rtype: The multilingual dataset is returned as dict,
          source and tgt vocabs.
  """

  dataset = {}
  CUR_DIR = os.getcwd()
  levels_up = 0
  if args.use_colab is not None:
    DATA_PATH = '/home2/aditya_hari/gsoc/data/processed'
  else:
    DATA_PATH = (os.path.normpath(os.path.join(*([CUR_DIR] + [".."] * levels_up)))) + '/data/processed_data/'

  # create vocabs for the source
  src_vocab = tf.keras.preprocessing.text.Tokenizer(filters='')
  target_str = ''
  source_str = ''
  spl_sym = DATA_PATH + 'special_symbols'

  if args.model == 'gat':
    for lang in languages:

      (dataset[lang + '_train_nodes'], dataset[lang + '_train_labels'],
       dataset[lang + '_train_node1'], dataset[lang + '_train_node2']) = PreProcess(DATA_PATH + lang + '/train_src',
                                                                                    lang)
      (dataset[lang + '_eval_nodes'], dataset[lang + '_eval_labels'],
       dataset[lang + '_eval_node1'], dataset[lang + '_eval_node2']) = PreProcess(DATA_PATH + lang + '/eval_src',
                                                                                  lang)
      (dataset[lang + '_test_nodes'], dataset[lang + '_test_labels'],
       dataset[lang + '_test_node1'], dataset[lang + '_test_node2']) = PreProcess(DATA_PATH + lang + '/test_src',
                                                                                  lang)
      train_tgt = io.open(DATA_PATH + lang + '/train_tgt', encoding='UTF-8').read().strip().split('\n')
      dataset[lang + '_train_tgt'] = [(PreProcessSentence(w, args.sentencepiece, lang)) for w in train_tgt]
      eval_tgt = io.open(DATA_PATH + lang + '/eval_tgt', encoding='UTF-8').read().strip().split('\n')
      dataset[lang + '_eval_tgt'] = [(PreProcessSentence(w, args.sentencepiece, lang)) for w in eval_tgt]
      target_str += (DATA_PATH + lang + '/train_tgt') + ','
      target_str += (DATA_PATH + lang + '/eval_tgt') + ','

      # fit the vocab
      src_vocab.fit_on_texts(dataset[lang + '_train_nodes'])
      src_vocab.fit_on_texts(dataset[lang + '_train_labels'])
      src_vocab.fit_on_texts(dataset[lang + '_train_node1'])
      src_vocab.fit_on_texts(dataset[lang + '_train_node2'])
      src_vocab.fit_on_texts(dataset[lang + '_eval_nodes'])
      src_vocab.fit_on_texts(dataset[lang + '_eval_labels'])
      src_vocab.fit_on_texts(dataset[lang + '_eval_node1'])
      src_vocab.fit_on_texts(dataset[lang + '_eval_node2'])

      if args.sentencepiece == 'False':
        src_vocab.fit_on_texts(dataset[lang + '_train_tgt'])
        src_vocab.fit_on_texts(dataset[lang + '_eval_tgt'])

    if args.sentencepiece == 'True':
      print('Tragers : ' + target_str)
      os.makedirs(('vocabs/{}/{}'.format(args.model, args.lang)), exist_ok=True)
      spm.SentencePieceTrainer.Train('--input={} --model_prefix=vocabs/{}/{}/train_vocab'
                                     ' --vocab_size={} --character_coverage=1.0 --model_type={}'.format(
        (target_str + spl_sym), args.model, args.lang,
        str(args.vocab_size), args.sentencepiece_model))
      sp = spm.SentencePieceProcessor()
      sp.load('vocabs/' + args.model + '/' + args.lang + '/train_vocab.model')

    if args.sentencepiece == 'True':
      return dataset, src_vocab, sp
    else:
      return dataset, src_vocab, src_vocab
  else:
    for lang in languages:
      train_src = io.open(DATA_PATH + lang + '/train_src', encoding='UTF-8').read().strip().split('\n')
      dataset[lang + '_train_src'] = [PreprocessSeqSource(w, args.sentencepiece, lang) for w in train_src]
      eval_src = io.open(DATA_PATH + lang + '/eval_src', encoding='UTF-8').read().strip().split('\n')
      dataset[lang + '_eval_src'] = [PreprocessSeqSource(w, args.sentencepiece, lang) for w in eval_src]
      train_tgt = io.open(DATA_PATH + lang + '/train_tgt', encoding='UTF-8').read().strip().split('\n')
      dataset[lang + '_train_tgt'] = [PreProcessSentence(w, args.sentencepiece, lang) for w in train_tgt]
      eval_tgt = io.open(DATA_PATH + lang + '/eval_tgt', encoding='UTF-8').read().strip().split('\n')
      dataset[lang + '_eval_tgt'] = [PreProcessSentence(w, args.sentencepiece, lang) for w in eval_tgt]
      test_src = io.open(DATA_PATH + lang + '/test_src', encoding='UTF-8').read().strip().split('\n')
      dataset[lang + '_test_src'] = [PreprocessSeqSource(w, args.sentencepiece, lang) for w in test_src]

      target_str += (DATA_PATH + lang + '/train_tgt') + ','
      target_str += (DATA_PATH + lang + '/eval_tgt') + ','
      source_str += (DATA_PATH + lang + '/train_src') + ','
      source_str += (DATA_PATH + lang + '/eval_src') + ','

      if args.sentencepiece == 'False':
        src_vocab.fit_on_texts(dataset[lang + '_train_tgt'])
        src_vocab.fit_on_texts(dataset[lang + '_eval_tgt'])
        src_vocab.fit_on_texts(dataset[lang + '_eval_tgt'])
        src_vocab.fit_on_texts(dataset[lang + '_eval_tgt'])

    if args.sentencepiece == 'True':
      print('Targets : ' + target_str)
      os.makedirs(('vocabs/{}/{}'.format(args.model, args.lang)), exist_ok=True)
      spm.SentencePieceTrainer.Train('--input={} --model_prefix=vocabs/{}/{}/train_vocab'
                                     ' --vocab_size={} --character_coverage=1.0 --model_type={}'.format(
        (target_str + spl_sym), args.model, args.lang,
        str(args.vocab_size), args.sentencepiece_model))
      sp = spm.SentencePieceProcessor()
      sp.load('vocabs/' + args.model + '/' + args.lang + '/train_vocab.model')

    if args.sentencepiece == 'True':
      return dataset, sp
    else:
      return dataset, src_vocab


def ProcessMultilingualDataset(args, set=None):
  """
  Takes in the prepocessed Datasets and converts them
  into tensorflow tensors, Adds padding to make the
  targets uniform and packages the individual datasets
  as a combined tf.data.Dataset object.
  Also shuffles and batches the dataset.

  Note : The datasets are not concatenated into one big
  dataset if Knowledge Distillation is being used. We would
  require all datasets seperately to pass each batch through
  both the teacher model and student model. Then the fucntion
  returns a dict with all datasets.

  :param args: Args obj which contains paths to the preprocessed files
  :type args: ArgParse object
  :return: The multilingual dataset along with source and targer vocabs
  and their sizes and maximum target sequence length.
  :rtype: tf.data.Dataset object, vocab objects (src and tgt vocab),
          int ( max sequence length ), int (total buffer size,
          int ( steps per epoch, not much used )
  """

  multilingual_dataset = {}
  TRAIN_BUFFER_SIZE = 0
  EVAL_BUFFER_SIZE = 0

  if args.model == 'gat':
    dataset, src_vocab, tgt_vocab = LoadMultlingualDataset(args)
    for lang in languages:
      if args.sentencepiece == 'False':
        dataset[lang + '_train_tgt'] = _tensorize(src_vocab, dataset[lang + '_train_tgt'])
        dataset[lang + '_eval_tgt'] = _tensorize(src_vocab, dataset[lang + '_eval_tgt'])

      else:
        dataset[lang + '_train_tgt'] = [tgt_vocab.encode_as_ids(w) for w in dataset[lang + '_train_tgt']]
        dataset[lang + '_train_tgt'] = tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_train_tgt'],
                                                                                     padding='post')
        dataset[lang + '_eval_tgt'] = [tgt_vocab.encode_as_ids(w) for w in dataset[lang + '_eval_tgt']]
        dataset[lang + '_eval_tgt'] = tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_eval_tgt'],
                                                                                    padding='post')

      for part in ['train', 'eval', 'test']:
        dataset[lang + '_' + part + '_nodes'] = padding(
          _tensorize(src_vocab, dataset[lang + '_' + part + '_nodes']), 16)
        dataset[lang + '_' + part + '_labels'] = padding(
          _tensorize(src_vocab, dataset[lang + '_' + part + '_labels']), 16)
        dataset[lang + '_' + part + '_node1'] = padding(
          _tensorize(src_vocab, dataset[lang + '_' + part + '_node1']), 16)
        dataset[lang + '_' + part + '_node2'] = padding(
          _tensorize(src_vocab, dataset[lang + '_' + part + '_node2']), 16)

      TRAIN_BUFFER_SIZE += (dataset[lang + '_train_nodes']).shape[0]
      EVAL_BUFFER_SIZE += (dataset[lang + '_eval_nodes']).shape[0]

    MaxSeqSize = max(dataset['eng_train_tgt'].shape[1],
                     dataset['ger_train_tgt'].shape[1],
                     dataset['rus_train_tgt'].shape[1])

    MULTI_BUFFER_SIZE = 0
    BATCH_SIZE = args.batch_size
    for lang in languages:
      dataset[lang + '_train_tgt'] = padding(
        tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_train_tgt'],
                                                      padding='post'), MaxSeqSize)
      dataset[lang + '_eval_tgt'] = padding(
        tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_eval_tgt'],
                                                      padding='post'), MaxSeqSize)

      BUFFER_SIZE = len(dataset[lang + '_train_tgt'])
      MULTI_BUFFER_SIZE += BUFFER_SIZE
      dataset_size = dataset[lang + '_train_tgt'].shape[0]

      for part in ['train', 'eval']:
        if part == 'train':
          multilingual_dataset[lang + '_' + part + '_set'] = tf.data.Dataset.from_tensor_slices(
            (dataset[lang + '_' + part + '_nodes'],
             dataset[lang + '_' + part + '_labels'],
             dataset[lang + '_' + part + '_node1'],
             dataset[lang + '_' + part + '_node2'],
             dataset[lang + '_' + part + '_tgt']))
          multilingual_dataset[lang + '_' + part + '_set'] = multilingual_dataset[
            lang + '_' + part + '_set'].shuffle(BUFFER_SIZE)
        else:
          multilingual_dataset[lang + '_' + part + '_set'] = tf.data.Dataset.from_tensor_slices(
            (dataset[lang + '_' + part + '_nodes'],
             dataset[lang + '_' + part + '_labels'],
             dataset[lang + '_' + part + '_node1'],
             dataset[lang + '_' + part + '_node2'],
             dataset[lang + '_' + part + '_tgt']))

      multilingual_dataset[lang + '_test_set'] = tf.data.Dataset.from_tensor_slices(
        (dataset[lang + '_test_nodes'],
         dataset[lang + '_test_labels'],
         dataset[lang + '_test_node1'],
         dataset[lang + '_test_node2']))

    final_dataset = {}
    for opt in ['train', 'test', 'eval']:
      final_dataset[opt + '_set'] = \
        multilingual_dataset['eng_' + opt + '_set'].concatenate(
          multilingual_dataset['ger_' + opt + '_set'].concatenate(
            multilingual_dataset['rus_' + opt + '_set']))

    if args.sentencepiece == 'False':
      src_vocab_size = len(src_vocab.word_index) + 1
      tgt_vocab_size = args.vocab_size
    else:
      src_vocab_size = len(src_vocab.word_index) + 1
      tgt_vocab_size = tgt_vocab.get_piece_size()

    final_dataset['train_set'] = final_dataset['train_set'].shuffle(MULTI_BUFFER_SIZE)
    final_dataset['train_set'] = final_dataset['train_set'].batch(BATCH_SIZE,
                                                                  drop_remainder=True)
    final_dataset['eval_set'] = final_dataset['eval_set'].batch(BATCH_SIZE,
                                                                drop_remainder=True)
    final_dataset['test_set'] = final_dataset['test_set'].batch(BATCH_SIZE,
                                                                drop_remainder=False)
    steps_per_epoch = int(MULTI_BUFFER_SIZE // BATCH_SIZE)

    print('BUFFER SIZE ' + str(MULTI_BUFFER_SIZE))
    print("Dataset shapes : ")

    return (final_dataset, src_vocab, src_vocab_size, tgt_vocab,
            tgt_vocab_size, MULTI_BUFFER_SIZE, steps_per_epoch, MaxSeqSize)

  else:
    dataset, vocab = LoadMultlingualDataset(args)
    for lang in languages:
      if args.sentencepiece == 'False':
        dataset[lang + '_train_src'] = _tensorize(vocab, dataset[lang + '_train_src'])
        dataset[lang + '_eval_src'] = _tensorize(vocab, dataset[lang + '_eval_src'])
        dataset[lang + '_train_tgt'] = _tensorize(vocab, dataset[lang + '_train_tgt'])
        dataset[lang + '_eval_tgt'] = _tensorize(vocab, dataset[lang + '_eval_tgt'])
        dataset[lang + '_test_src'] = _tensorize(vocab, dataset[lang + '_eval_tgt'])

      else:
        dataset[lang + '_train_src'] = [vocab.encode_as_ids(w) for w in dataset[lang + '_train_src']]
        dataset[lang + '_train_src'] = tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_train_src'],
                                                                                     padding='post')
        dataset[lang + '_eval_src'] = [vocab.encode_as_ids(w) for w in dataset[lang + '_eval_src']]
        dataset[lang + '_eval_src'] = tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_eval_src'],
                                                                                    padding='post')

        dataset[lang + '_train_tgt'] = [vocab.encode_as_ids(w) for w in dataset[lang + '_train_tgt']]
        dataset[lang + '_train_tgt'] = tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_train_tgt'],
                                                                                     padding='post')
        dataset[lang + '_eval_tgt'] = [vocab.encode_as_ids(w) for w in dataset[lang + '_eval_tgt']]
        dataset[lang + '_eval_tgt'] = tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_eval_tgt'],
                                                                                    padding='post')
        dataset[lang + '_test_src'] = [vocab.encode_as_ids(w) for w in dataset[lang + '_test_src']]
        dataset[lang + '_test_src'] = tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_test_src'],
                                                                                    padding='post')

      TRAIN_BUFFER_SIZE += (dataset[lang + '_train_src']).shape[0]
      EVAL_BUFFER_SIZE += (dataset[lang + '_eval_src']).shape[0]

    MaxSeqSize = max(dataset['eng_train_tgt'].shape[1],
                     dataset['ger_train_tgt'].shape[1],
                     dataset['rus_train_tgt'].shape[1])
    SrcSeqSize = max(dataset['eng_train_src'].shape[1],
                     dataset['ger_train_src'].shape[1],
                     dataset['rus_train_src'].shape[1])
    TestSeqSize = max(dataset['eng_test_src'].shape[1],
                      dataset['ger_test_src'].shape[1],
                      dataset['rus_test_src'].shape[1])

    MULTI_BUFFER_SIZE = 0
    BATCH_SIZE = args.batch_size
    for lang in languages:
      dataset[lang + '_train_src'] = padding(
        tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_train_src'],
                                                      padding='post'), SrcSeqSize)
      dataset[lang + '_eval_src'] = padding(
        tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_eval_src'],
                                                      padding='post'), SrcSeqSize)

      dataset[lang + '_train_tgt'] = padding(
        tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_train_tgt'],
                                                      padding='post'), MaxSeqSize)
      dataset[lang + '_eval_tgt'] = padding(
        tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_eval_tgt'],
                                                      padding='post'), MaxSeqSize)
      dataset[lang + '_test_src'] = padding(
        tf.keras.preprocessing.sequence.pad_sequences(dataset[lang + '_test_src'],
                                                      padding='post'), TestSeqSize)

      BUFFER_SIZE = len(dataset[lang + '_train_tgt'])
      MULTI_BUFFER_SIZE += BUFFER_SIZE

      for part in ['train', 'eval']:
        if part == 'train':
          multilingual_dataset[lang + '_' + part + '_set'] = tf.data.Dataset.from_tensor_slices(
            (dataset[lang + '_' + part + '_src'],
             dataset[lang + '_' + part + '_tgt']))
          multilingual_dataset[lang + '_' + part + '_set'] = multilingual_dataset[
            lang + '_' + part + '_set'].shuffle(BUFFER_SIZE)
        else:
          multilingual_dataset[lang + '_' + part + '_set'] = tf.data.Dataset.from_tensor_slices(
            (dataset[lang + '_' + part + '_src'],
             dataset[lang + '_' + part + '_tgt']))

      multilingual_dataset[lang + '_test_set'] = tf.data.Dataset.from_tensor_slices(
        dataset[lang + '_test_src'])

    final_dataset = {}
    for opt in ['train', 'test', 'eval']:
      final_dataset[opt + '_set'] = \
        multilingual_dataset['eng_' + opt + '_set'].concatenate(
          multilingual_dataset['ger_' + opt + '_set'].concatenate(
            multilingual_dataset['rus_' + opt + '_set']))

    if args.sentencepiece == 'False':
      tgt_vocab_size = args.vocab_size
    else:
      tgt_vocab_size = vocab.get_piece_size()

    final_dataset['train_set'] = final_dataset['train_set'].shuffle(MULTI_BUFFER_SIZE)
    final_dataset['train_set'] = final_dataset['train_set'].batch(BATCH_SIZE,
                                                                  drop_remainder=True)
    final_dataset['eval_set'] = final_dataset['eval_set'].batch(BATCH_SIZE,
                                                                drop_remainder=True)
    final_dataset['test_set'] = final_dataset['test_set'].batch(BATCH_SIZE,
                                                                drop_remainder=False)
    steps_per_epoch = int(MULTI_BUFFER_SIZE // BATCH_SIZE)

    print('BUFFER SIZE ' + str(MULTI_BUFFER_SIZE))
    print("Dataset shapes : ")

    return (final_dataset, vocab, tgt_vocab_size,
            MULTI_BUFFER_SIZE, steps_per_epoch, MaxSeqSize)
