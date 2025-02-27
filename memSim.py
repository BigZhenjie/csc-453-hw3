import sys
from collections import deque
from LRUCache import LRUCache

def preprocess_opt(addresses):
    next_use = {}  # Maps page to list of future access indices
    for idx, addr in enumerate(addresses):
        page = addr // 256
        if page not in next_use:
            next_use[page] = []
        next_use[page].append(idx)
    return next_use

def get_farthest_next_use(frame_to_page, next_use, current_index):
    farthest_frame = -1
    farthest_index = -1
    for frame, page in enumerate(frame_to_page):
        if page is None:
            continue
        if page not in next_use or not next_use[page]:
            # Page has no future use, evict it
            return frame
        # Find the next use of this page
        next_index = next_use[page][0]
        if next_index > farthest_index:
            farthest_index = next_index
            farthest_frame = frame
    return farthest_frame

def main():
    # Default arguments if none are provided
    DEFAULT_FRAMES = 256
    DEFAULT_PRA = "FIFO"

    # Parse arguments
    ref_file = sys.argv[1] if len(sys.argv) > 1 else None
    frames = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_FRAMES
    pra = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PRA
    
    # Read addresses and preprocess for OPT
    with open(ref_file, 'r') as f:
        addresses = [int(line.strip()) for line in f]

    if pra == "OPT":
        next_use = preprocess_opt(addresses)
    
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
    for idx, addr in enumerate(addresses):
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
                    elif pra == "OPT":
                        # Evict the frame with the farthest next use
                        free_frame = get_farthest_next_use(frame_to_page, next_use, idx)
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
        byte_value = physical_memory[frame][offset]
        frame_content = physical_memory[frame].hex().upper()
        print(f"{addr}, {byte_value}, {frame}, \n{frame_content}")
            
    
    # Print statistics
    tlb_misses = len(addresses) - tlb_hits
    tlb_hit_rate = (tlb_hits / len(addresses)) * 100
    page_fault_rate = (page_faults / len(addresses)) * 100
    print(f"Number of Translated Addresses = {len(addresses)}")
    print(f"Page Faults = {page_faults}")
    print(f"Page Fault Rate = {page_faults / len(addresses):.3f}")
    print(f"TLB Hits = {tlb_hits}")
    print(f"TLB Misses = {tlb_misses}")
    print(f"TLB Hit Rate = {tlb_hit_rate:.3f}")

if __name__ == "__main__":
    main()