import sys
from collections import deque
from LRUCache import LRUCache

def main():
    # Parse arguments
    ref_file, frames, pra = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    
    # Read addresses and preprocess for OPT
    with open(ref_file, 'r') as f:
        addresses = [int(line.strip()) for line in f]
    
    # Initialize structures
    tlb = deque(maxlen=16)
    page_table = [{'present': False, 'frame': None} for _ in range(256)]
    physical_memory = [bytearray(256) for _ in range(frames)]
    frame_to_page = [None] * frames
    load_time = [0] * frames  # FIFO
    lru_queue = LRUCache(frames)  # LRU
    global_time = 0
    
    # Process addresses
    page_faults = tlb_hits = 0
    for addr in (addresses):
        page = addr // 256
        offset = addr % 256
        
        # TLB/Page Table lookup
        frame = None
        tlb_hit = False
        #check if page is in TLB
        for entry in list(tlb):
            if entry['page'] == page:
                frame = entry['frame']
                if pra == "LRU":
                    lru_queue.get(frame)
                tlb_hits += 1
                tlb_hit = True
                break
        
        #if not hit
        if not tlb_hit:
            if page_table[page]['present']:
                #means page is in page table & also need to append to TLB
                frame = page_table[page]['frame']
                tlb.append({'page': page, 'frame': frame})
            else:
                #----------------------!!!PAGE FAUL ALERT!!!-------------------
                page_faults += 1
                free_frame = None

                #need to find a free frame
                for frame in range(frames):
                    if frame_to_page[frame] is None:
                        #we found a free frame!
                        free_frame = frame
                        break
                
                #no free frame? we are COOKED
                #jk, we need to evict someting :(
                if free_frame is None:
                    if pra == "FIFO":
                        #this is just using the loading time as the key
                        #and getting the frame with the lowest load time
                        free_frame = min(range(frames), key=lambda x: load_time[x])
                    elif pra == "LRU":
                        # evict the frame at the end of the LRU queue
                        free_frame = lru_queue.pop()
                    else:
                        print("Invalid PRA")
                    #evict this frame
                    evicted_page = frame_to_page[free_frame]
                    page_table[evicted_page]['present'] = False

                    #also need to update the TLB
                    for entry in list(tlb):
                        if entry['page'] == evicted_page:
                            tlb.remove(entry)
                            break
                # load new page from backing store
                with open('BACKING_STORE.bin', 'rb') as f:
                    f.seek(page * 256)
                    physical_memory[free_frame] = bytearray(f.read(256))

                # update metadata
                frame_to_page[free_frame] = page
                page_table[page] = {'present': True, 'frame': free_frame}
                #update load time for FIFO
                load_time[free_frame] = global_time
                #update last used for LRU
                if pra == "LRU":
                    lru_queue.put(free_frame)
                global_time += 1
                frame = free_frame

                # update TLB
                tlb.append({'page': page, 'frame': frame})


        # --- Output ---
        print(f"Address: {addr}, Page: {page}, Frame: {frame}")
            
    
    # Print statistics
    print(f"Page faults: {page_faults}")

if __name__ == "__main__":
    main()