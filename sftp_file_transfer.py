import paramiko
import os


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

def ensure_remote_dir(remote_dir):
    """Ensure that the remote directory exists, creating it if necessary."""
    dirs = remote_dir.strip("/").split("/")
    path = ""
    for directory in dirs:
        path += f"/{directory}"
        try:
            sftp.stat(path)  # Check if directory exists
        except FileNotFoundError:
            sftp.mkdir(path)  # Create if it doesn't exist

def upload_directory(local_dir, remote_dir):
    """Recursively upload a folder to SFTP."""
    # print(remote_dir)
    # try:
    #     sftp.mkdir(remote_dir)
    #     print('remote folder created with success')
    # except IOError:  # Folder might already exist
    #     print('did not work!')
    #     pass

    ensure_remote_dir(remote_dir)

    for item in os.listdir(local_dir):
        local_item = os.path.join(local_dir, item)
        remote_item = f"{remote_dir}/{item}"

        if os.path.isdir(local_item):
            upload_directory(local_item, remote_item)  # Recursion for subfolders
        else:
            sftp.put(local_item, remote_item)
            print(f"Uploaded: {local_item} -> {remote_item}")


sftp, transport=connect_sftp()

# pi_list=['AYL_2D', 'WATER_INTAKES_2D', 'WASTE_WATER_2D',
#          'ROADS_2D', 'SHORE_PROT_STRUC_1D', 'ERIW_MIN_1D',
#          'TURTLE_1D', 'ZIPA_1D',
#          'ERIW_MIN_2D', 'IERM_2D', 'SAUV_2D',
#          'CHNI_2D', 'IXEX_RPI_2D', 'ONZI_OCCUPANCY_1D']

pi_list=['PIKE_2D']

local_folder=r'P:\GLAM\Dashboard\ISEE_Dash_portable\ISEE_POST_PROCESS_DATA_3'
remote_folder='/ISEE_POST_PROCESS_DATA_3'

for pi in pi_list:

    try:
        sftp.mkdir(os.path.join(local_folder, pi))
    except IOError:  # Folder might already exist
        pass

    try:
        sftp.mkdir(os.path.join(local_folder, pi, 'YEAR'))
    except IOError:  # Folder might already exist
        pass

    try:
        sftp.mkdir(os.path.join(local_folder, pi, 'YEAR', 'PLAN'))
    except IOError:  # Folder might already exist
        pass

    src1 = os.path.join(local_folder, pi, 'YEAR', 'PLAN')


    dst1=f'{remote_folder}/{pi}/YEAR/PLAN'
    #dst1=dst1.replace('\\', '/')
    upload_directory(src1, dst1)

    try:
        sftp.mkdir(os.path.join(local_folder, pi, 'YEAR', 'SECTION'))
    except IOError:  # Folder might already exist
        pass

    src2=os.path.join(local_folder, pi, 'YEAR', 'SECTION')
    dst2=f'{remote_folder}/{pi}/YEAR/SECTION'
    #dst2 = dst2.replace('\\', '/')
    upload_directory(src2, dst2)

quit()