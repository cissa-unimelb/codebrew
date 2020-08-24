# Model validation using snp vectors 
import os
import pandas
import gzip
import subprocess

def create_csv_compendium(path):
    # read all snp compendium files into a single csv file 
    # takes a while to run, run on multiple cores if possible
    snp_files = sorted(glob.glob(path+'compendium/*.gz'))
    headers = ['chr','start','end','motif','footprint_score_lr','strand','ref_priorlodds',
                    'alt_priorlodds','ref_allele','alt_allele','effect']

    if os.path.exists(path+'validation/all_snp_compendium.csv'):
        print("compendium dataset already read at {}".format(path+'validation/all_snp_compendium.csv'))
        return

    all_snps = pd.DataFrame(columns = headers)
    for snp_file in snp_files:
        f = gzip.open(snp_file)
        df = pd.read_csv(f,delimiter='\t',names=headers)
        all_snps = pd.concat([all_snps,df], axis=0, ignore_index=True)
        print(all_snps.shape)
        
    all_snps.drop_duplicates(inplace=True)
    all_snps.to_csv(path+'validation/all_snp_compendium.csv',header=headers,index=False,sep='\t')


def read_unqiue_snps_compendium(path):
    if os.path.exists(path+'validation/all_snp_unique.csv'):
        print("all unique snps already read at {}".format(path+'validation/all_snp_unique.csv'))
        return

    # get all unique snps. This only includes the chromosome, start and end without the other columns
    df = pd.read_csv('data/validation/all_snp_compendium.csv', delimiter='\t')
    # drop all other columns except for the ones that define the snp
    df_all_unique = df.iloc[:,0:3]
    df_all_unique.drop_duplicates(inplace=True)

    df_all_unique.to_csv(path+'validation/all_snp_unique.csv',index=False,sep='\t')


def get_common_snps_compendium(path):
    # find all common snps bewteen the dsQTL file and the compendium files. Include compendium.

    if os.path.exists(path+'validation/common_snp_compendium.csv'):
        print("common snps already read at {}".format(path+'validation/common_snp_compendium.csv'))
        return

    df_dsQTL = pd.read_csv(path+'dsQTL.eval.txt',delimiter='\t')
    df_dsQTL.set_index(['chr','pos0','pos'],inplace=True)

    df_compendium = pd.read_csv(path+'validation/all_snp_compendium.csv',delimiter='\t')
    df_compendium.set_index(['chr','start','end'],inplace=True)

    common_snps_index = df_compendium.index.intersection(df_dsQTL.index)

    common_snps = df_compendium.loc[common_snps_index,:]
    common_snps.reset_index(inplace=True)
    print(common_snps.shape)
    common_snps.to_csv(path+'validation/common_snp_compendium.csv',index=False, sep='\t')



def get_common_snps_unique(path):
    # get all unique snps that are common bewteen the dsQTL file and the compendium files. 
    # This only includes the chromosome, start and end without the other columns
    # make true dsQTL labels and gkmSVM labels for all SNP common in the compendium and dsQTL file

    if os.path.exists(path+'validation/common_snp_unique.csv'):
        print("common unique snps already read at {}".format(path+'validation/common_snp_unique.csv'))
        return

    df = pd.read_csv(path+'validation/common_snp_compendium.csv', delimiter='\t')

    df_valid_unique = df.iloc[:,0:3]
    df_valid_unique.drop_duplicates(inplace=True)
    df_valid_unique.set_index(['chr','start','end'],inplace=True)


    df_labels = pd.DataFrame(columns=['dsQTL_labels'])
    df_gkmsvm =pd.DataFrame(columns=['gkmSVM_labels'])

    df_dsQTL = pd.read_csv(path+'dsQTL.eval.txt',delimiter='\t')
    df_dsQTL.set_index(['chr','pos0','pos'],inplace=True)

    # get true labels for all common snps
    #common_ind = df_dsQTL.index.intersection(df_valid_unqiue.index)
    df_dsQTL_labels = df_dsQTL.loc[df_valid_unique.index,'label']
    df_labels['dsQTL_labels'] = df_dsQTL_labels
    df_labels.to_csv(path+'validation/common_snp_true_labels.csv',sep='\t',index=False)


    # get gkmSVM labels for all common snps
    gkmSVM_labels = df_dsQTL.loc[df_valid_unique.index,'abs_gkm_SVM']
    df_gkmsvm['gkmSVM_labels'] = gkmSVM_labels
    df_gkmsvm.to_csv(path+'validation/common_snp_gkmSVM_labels.csv',sep='\t',index=False)


    df_valid_unqiue.reset_index(inplace=True)
    df_valid_unqiue.to_csv(path+'validation/common_snp_unique.csv',index=False, sep='\t')



def make_snp_footprint_matrix(path):
    # make snp vectors(A matrix) - a snp vector is a binary vector, each entry corresponds a specific motif.
    # Entry is 1 if that motifs that overlap with the snp, 0 otherwise. (Similar to how we built training matrix)
    motif_files = sorted(glob.glob(path+'combo/*.gz'))
    
    headers = ['chr','start','end']
    df = pd.read_csv(path+'validation/common_snp_unique.csv',sep='\t')

    if len(df.columns) > 3:
        print("snp footprint matrix already made at {}".format(path+'validation/common_snp_unique.csv'))
        return

    for idx,motif in enumerate(motif_files):
        motif_name = re.compile('.*/(.*).combo.bed.gz').search(motif).group(1)
        cmd_str = "bedtools intersect -a {}validation/common_snp_unique.csv -b {} -c | cut -f 4".format(path,motif)
        out = subprocess.check_output(cmd_str,shell=True)
        # convert numbers from string to integers. Last line is empty so don't include
        footprint = map(int,out.split('\n')[:-1])
        footprint = (np.array(footprint) >=1).astype(int)
        headers.append(motif_name)
        print("{}: {}, count of 1's: {}".format(motif_name, sum(footprint),Counter(footprint)[1]))
        df[motif_name] = footprint
    df.to_csv(path+'validation/common_snp_unique.csv',index=False, header = headers, sep='\t')
    

# make reference/alternate matrix that is to be fed into the NN. Each row is a unique SNP with its motif footprint 
def make_ref_alt_matrix(path, allele='ref'):

    if os.path.exists(path+'common_snp_unique_{}.csv'.format(allele)):
        print("{} matrix already read at {}".format(allele, path+'common_snp_unique_{}.csv'.format(allele)))
        return

    df_compendium = pd.read_csv(path+'common_snp_compendium.csv',sep='\t')
    df_validation = pd.read_csv(path+'common_snp_unique.csv',sep='\t')

    df_compendium.set_index(['chr','start','end'],inplace=True)
    df_validation.set_index(['chr','start','end'],inplace=True)
    
    # only interested in rows where the motif has an effect on binding (effect = 2)
    df_compendium = df_compendium.loc[df_compendium['effect']==2]

    ref_priorlodds = np.array(df_compendium['ref_priorlodds'])
    alt_priorlodds = np.array(df_compendium['alt_priorlodds'])
    if allele=='ref':
        # if ref_priorlodds-alt_priorlodds is greater than 0, reference allele increases binding
        df_compendium['binding_direction'] = (ref_priorlodds-alt_priorlodds > 0).astype(int)
    else:
        # if ref_priorlodds-alt_priorlodds less than 0, alternate allele increases binding
        df_compendium['binding_direction'] = (ref_priorlodds-alt_priorlodds <= 0).astype(int)

        
    for index in df_validation.index.values:
        try:
            centisnp = df_compendium.loc[index,['motif','binding_direction']]
        except:
            continue
        for motif in centisnp.values:
            motif_name, binding_direction = motif
            # only consider motifs that overlap with the snp
            if df_validation.at[index,motif_name] == 1:
                df_validation.at[index,motif_name] = binding_direction

    df_validation.reset_index(inplace=True)
    df_compendium.reset_index(inplace=True)
    df_validation.to_csv(path+'common_snp_unique_{}.csv'.format(allele),index=False, sep='\t')


def driver(ROOT_DIR):
    path = ROOT_DIR + 'data/'
    create_csv_compendium(path)
    read_unqiue_snps_compendium(path)
    get_common_snps_compendium(path)
    get_common_snps_unique(path)
    make_snp_footprint_matrix(path)
    make_ref_alt_matrix(path+'validation/',allele='ref')
    make_ref_alt_matrix(path+'validation/',allele='alt')