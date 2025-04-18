#NECESSARY IMPORTS
import binascii
import zlib
import os

#TO READ HEXADECIMAL BYTE DATA FROM THE HARD/SSD DRIVE
def read_sectors(drive_path, num_sectors, sector_size=512):
    try:
        with open(drive_path, 'rb') as f:
            data = f.read(num_sectors * sector_size)
            return binascii.hexlify(data).decode('ascii').upper()
    except Exception as e:
        print(f"Error reading drive: {e}")
        return None

physical_drive = r'\\.\PhysicalDrive0'
num_sectors_to_read = 34
hexes = read_sectors(physical_drive, num_sectors_to_read)
hexes = hexes.replace(' ','')
hexes = hexes.replace('\n', '')

#BREAKING DOWN THE SECTIONS
Protective_MBR = hexes[:1024]
GPT_Header = hexes[1024:1208]
Partition_Array = hexes[2048:]

#CONVERTS THE LITTLE ENDIAN TO NORMAL
def endian_to_normal(little):
    y = ''
    for i in range(0, len(little), 2):
        y += little[len(little) - 2 - i:len(little) - i]
    return y

#BREAKS DOWN THE GPT HEADER INTO HUMAN READABLE FORMAT
def gpt_header_distro(header, Partition_Array):
    signature = binascii.unhexlify(header[:16]).decode('utf-8')
    header_bytes = endian_to_normal(header[24:32])
    header_checksum = endian_to_normal(header[32:40])
    header_sector = endian_to_normal(header[48:64])
    backup_sector = endian_to_normal(header[64:80])
    first_lba = endian_to_normal(header[80:96])
    last_lba = endian_to_normal(header[96:112])
    guid = f"{endian_to_normal(header[112:120])}-{endian_to_normal(header[120:124])}-{endian_to_normal(header[124:128])}-{header[128:144]}"
    entry_lba = endian_to_normal(header[144:160])
    entries = endian_to_normal(header[160:168])
    sizes = endian_to_normal(header[168:176])
    partition_checksum = endian_to_normal(header[176:184])
    pc = hex(zlib.crc32(binascii.unhexlify(Partition_Array)))[2:].upper()
    hc = hex(zlib.crc32(binascii.unhexlify(header[:32]+'00000000'+header[40:176]+endian_to_normal(partition_checksum))))[2:].upper()
    
    print(f"Signature: {signature}")
    print(f"Header Length: {int(header_bytes, 16)} bytes")
    print(f"Header Checksum: {hc}")
    print(f"Current sector: {int(header_sector, 16)}")
    print(f"Backup header sector: {int(backup_sector, 16)}")
    print(f"First drive sector: {int(first_lba, 16)}")
    print(f"Last drive sector: {int(last_lba, 16)}")
    print(f"Disk GUID: {guid}")
    print(f"Partition Entry sector: {int(entry_lba, 16)}")
    print(f"Entries: {int(entries, 16)}")
    print(f"Size of each entry: {int(sizes, 16)}")
    print(f"Partition Checksum: {partition_checksum}\n")
    
    #MAKE SURE THAT THE HEADER OR THE PARTITION ARRAY ARE NOT CORRUPTED OR TAMPERED WITH
    if header_checksum == hc:
        print("Header Checksum match, therefore everything is intact.")
    else:
        print("Either the header or the partition is corrupted or tampered with.\n")
    
    if partition_checksum == pc:
        print("Partition checksums match, therefore partition array is intact.\n")
    else:
        print("Partition checksums don't match, the array is corrupter or tampered with.\n")

#BREAKS DOWN THE BYTE DISTRIBUTION OF THE PARTITION ARRAY
def partitions(Partition_Array):
    j = 1
    for i in range(0, len(Partition_Array), 256):
        partis = Partition_Array[i:i+256]
        if partis.count('0') == 256:
            continue
        else:
            print(f"Details of Partition {j}:")
            print(f"Partition type GUID: {endian_to_normal(partis[:8])}-{endian_to_normal(partis[8:12])}-{endian_to_normal(partis[12:16])}-{partis[16:32]}")
            print(f"Unique Partition GUID: {endian_to_normal(partis[32:40])}-{endian_to_normal(partis[40:44])}-{endian_to_normal(partis[44:48])}-{partis[48:64]}")
            start = int(endian_to_normal(partis[64:80]),16)
            end = int(endian_to_normal(partis[80:96]),16)
            print(f"Starting Sector: {start}")
            print(f"Ending Sector: {end}")
            print(f"Size of the Drive in bytes: {(end - start)*512}")
            print(f"Attributes: {endian_to_normal(partis[96:112])}")
            print(f"Partition Name: {binascii.unhexlify(partis[112:]).decode('utf-16')}\n")
            j += 1
            
#CHECKS THE TYPE OF DRIVE
if Protective_MBR[902:904] == 'FE':
    print("This is a GPT Drive\n")
    gpt_header_distro(GPT_Header, Partition_Array)
    partitions(Partition_Array)
else:
    print('Enter hexadecimal values of a GPT Drive!')
