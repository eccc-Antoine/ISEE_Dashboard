import paramiko
import pandas as pd

hostname = 'sanijcfilesharingprod.blob.core.windows.net'
port = 22
username = 'sanijcfilesharingprod.amaranda'
password = 'fk8alyBfLpgSz+8zh/3Qq1UqKcqYoyiG'


def connect_sftp():
    try:
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return sftp, transport


def sftp_close(sftp, transport):
    sftp.close()
    transport.close()


def read_from_sftp(filepath, sftp):
    filepath = filepath.replace('\\', '/')
    print(filepath)
    try:
        with sftp.open(filepath, 'r') as remote_file:
            df = pd.read_feather(remote_file)
            print(df.head())

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return df

sftp, transport=connect_sftp()

df=read_from_sftp('/ISEE_POST_PROCESS_DATA/BUILD_2D/YEAR/PLAN/Bv7baseline_v20240115/BUILD_2D_YEAR_Bv7baseline_v20240115_1980_2019.feather', sftp)

sftp_close(sftp, transport)

quit()