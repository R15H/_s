
/*NOTES






name conventions
global_PID_MACHINE_TIMESTAMP.bin
inst_ ...





*/
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

char destination_folder[512];
/*
struct FinalMetrics{
    uint32_t address;
    uint16_t totalTime ;
    uint16_t stallTime ;
    uint16_t lastStallTime ; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference
    uint16_t stallCyclesMLPLoad ; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference
    uint64_t start_cycle ; // at EA
    uint16_t stallCyclesMLPStore ;
    uint16_t stallCyclesMLPBoth ;

    uint8_t MLP_store_at_start   ;
    uint8_t MLP_store_at_end  ;
    uint8_t MLP_load_at_start  ;
    uint8_t MLP_load_at_end ;
    bool isMicroop : 1;
    bool tlb_miss : 1;
    bool isLoad : 1;
    bool isStore : 1;
};
*/

#define SPLIT_STRUCT_STAT_FIELDS(struct_name, field_name, type) \
    sprintf(filename, "%s_" #struct_name "_" #field_name "_%d.txt", destination_folder, run_number); \
    file = fopen(filename, "w"); \
    if (file == NULL){ \
        printf("Error opening file\n"); \
        return; \
    }\
    for (int i = 0; i < global_stat_bound; i++){ \
        fwrite(&struct_name[i].field_name, sizeof(type), 1, file); \
    }\
    fclose(file);\
    ;

// same macro again, but for the bool fields that have only 1 bit each
#define SPLIT_STRUCT_STAT_BIT_FIELD(struct_name, field_name, type) \
    sprintf(filename, "%s_" #struct_name "_" #field_name "_%d.txt", destination_folder, run_number); \
    file = fopen(filename, "w"); \
    if (file == NULL){ \
        printf("Error opening file\n"); \
        return; \
    }\
    for (int i = 0; i < global_stat_bound; i++){ \
        fwrite(&struct_name[i].field_name, sizeof(uint8_t), 1, file); \
    }\
    fclose(file);\
    ;

    struct FinalMetrics{
    //uint64_tI accessedMemory;
    uint64_t address;
    uint16_t totalTime;
    uint16_t stallTime;
    uint16_t L3stallTime;
    uint16_t lastStallTime;
    uint32_t stallCyclesMLPBoth;
    uint32_t stallCyclesMLPLoad;
    uint32_t stallCyclesMLPStore;
    uint32_t L3stallCyclesMLPLoad;

    uint8_t MLP_store_at_start;
    uint8_t MLP_store_at_end;
    uint8_t MLP_load_at_start;
    uint8_t MLP_load_at_end;

    uint8_t L3MLP_store_at_start;
    uint8_t L3MLP_store_at_middle;
    uint8_t L3MLP_store_at_end;
    uint8_t L3MLP_load_at_start;
    uint8_t L3MLP_load_at_middle;
    uint8_t L3MLP_load_at_end;
    uint8_t isMicroop;
    uint8_t tlb_miss;
    uint8_t isLoad;
    uint8_t isStore;
    uint8_t average_l3mlp;
    uint8_t average_mlp;

    uint64_t start_cycle;
};


struct InstructionData {
       uint64_t address;
    uint64_t count;
    uint64_t stallTime;
    uint64_t L3stallTime;
    uint64_t totalTime;
    uint64_t lastStallTime;
    uint64_t L3MLP_load_at_end;
    uint64_t MLP_load_at_end;
    uint64_t MLP_store_at_end;
    uint64_t L3MLP_store_at_end;
    uint64_t L3MLP_store_at_middle;
    uint64_t L3MLP_load_at_middle;
    uint64_t stallCyclesMLPLoad;
    uint64_t L3stallCyclesMLPLoad;
    uint64_t stallCyclesMLPStore;
    uint64_t stallCyclesMLPBoth;
    uint8_t accessBracket;
    bool tlbMiss;
};
/*
struct FinalMetrics{
     uint64_t accessedMemory = 0; 
    uint64_t address;
    uint16_t totalTime ;
    uint16_t stallTime ;
    uint16_t L3stallTime ;
    uint16_t lastStallTime; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference
    uint64_t stallCyclesMLPBoth ;
    uint64_t stallCyclesMLPLoad ;
    uint64_t stallCyclesMLPStore;
    uint64_t L3stallCyclesMLPLoad;
    //uint16_t stallCyclesMLPLoad = 0; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference
    //uint16_t stallCyclesMLPStore = 0;
    //uint16_t stallCyclesMLPBoth = 0;
    //uint16_t L3stallCyclesMLPLoad = 0; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference

    uint8_t MLP_store_at_start;
    uint8_t MLP_store_at_end;
    uint8_t MLP_load_at_start;
    uint8_t MLP_load_at_end;

    uint8_t L3MLP_store_at_start;
    uint8_t L3MLP_store_at_middle; // aka at the middle of the request
    uint8_t L3MLP_store_at_end ;
    uint8_t L3MLP_load_at_start ;

    uint8_t L3MLP_load_at_middle; // aka at the middle of the request
    uint8_t L3MLP_load_at_end;
    uint8_t isMicroop;
    uint8_t tlb_miss;
    uint8_t isLoad ;
    uint8_t isStore ;

    uint64_t start_cycle ; // at EA
};
*/

/*
struct FinalMetrics{
    uint64_t address; ////////////// CHANGED
    uint16_t totalTime;
    uint16_t stallTime;
    uint16_t L3stallTime ;
    uint16_t lastStallTime; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference

    uint32_t stallCyclesMLPBoth = 0;
    uint32_t stallCyclesMLPLoad = 0;
    uint32_t stallCyclesMLPStore = 0;
    uint32_t L3stallCyclesMLPLoad = 0;

    uint16_t stallCyclesMLPLoad; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference
    uint16_t stallCyclesMLPStore;
    uint16_t stallCyclesMLPBoth ;
    uint16_t L3stallCyclesMLPLoad; // First these store the cycles at start, then, we grab the end on the cpu and these store the difference

    uint8_t MLP_store_at_start  ;
    uint8_t MLP_store_at_end  ;
    uint8_t MLP_load_at_start;
    uint8_t MLP_load_at_end;

    uint8_t L3MLP_store_at_start ;
    uint8_t L3MLP_store_at_middle; // aka at the middle of the request
    uint8_t L3MLP_store_at_end ;
    uint8_t L3MLP_load_at_start;
    uint8_t L3MLP_load_at_middle; // aka at the middle of the request
    uint8_t L3MLP_load_at_end;

    bool isMicroop : 1;
    bool tlb_miss : 1;
    bool isLoad : 1;
    bool isStore : 1;
    uint64_t start_cycle; // at EA

};
    */

/*
struct GlobalStatsss{
    float stallCyclesMLPLoad;
    float stallCyclesMLPStore;
    float stallCyclesMLPBoth;
    uint64_t stalledCycles;
    uint64_t stalledCyclesDuringStore;
    uint64_t stalledCyclesWithMemRequests;
    uint64_t stalledCyclesWithStores;
    uint64_t cyclesWithMemrequests; // the diff between 2 = A1 of SOAR
    uint64_t commitedStores ;
    uint64_t commitedLoads ;  // The dif betweeen 2 = A2
    uint64_t commitedAtomic ;
    uint64_t commitedInstructions ;
    uint64_t totalSquashed ;
    uint64_t lastStallTime ;
    uint64_t currentCycle ;
    uint64_t loadCountByLatency[16];
    uint64_t tlbMisses;
};
*/

struct GlobalStatsss{

    uint64_t totalStalledCyclesSummed; 
    uint64_t totalL3StalledCyclesSummed; 
    uint64_t totalL3MLPStalledCyclesSummed; 
    uint64_t totalMLPStalledCyclesSummed; 

    uint64_t totalL3MLPsummed;
    uint64_t totalMLPsummed;
    uint64_t totalAccessTimeSummed; 
    uint64_t totalL3AccessTimeSummed; 
    uint64_t commitedL3Misses; 
     uint64_t totalL3MLP_D_TotalAccessTimeSummed; 
     uint64_t totalL3_D_TotalAccessTimeSummed;  // L333 stalls 
     uint64_t totalMLPStalledCycles_D_TimeSummed;

    uint64_t totalL3StallSummed; 


    uint64_t stallCyclesMLPLoad;
    uint64_t stallCyclesMLPStore;
    uint64_t stallCyclesMLPBoth;
    uint64_t stalledCycles;
    uint64_t stalledCyclesDuringStore;
    uint64_t stalledCyclesWithMemRequests;
    uint64_t stalledCyclesWithStores;
    uint64_t cyclesWithMemrequests; // the diff between 2 = A1 of SOAR
    uint64_t commitedStores;
    //uint64_t commitedL3Loads;  // The dif betweeen 2 = A2
    uint64_t commitedLoads;  // The dif betweeen 2 = A2
    uint64_t commitedAtomic;
    uint64_t commitedInstructions;
    uint64_t totalSquashed;
    uint64_t lastStallTime;
    uint64_t currentCycle;
    uint64_t loadCountByLatency[16];
    uint64_t tlbMisses;

    uint64_t onlyLoadsStalled;
    uint64_t onlyStoresStalled;
    uint64_t L3onlyLoadsStalled;
    uint64_t L3onlyStoresStalled;

    uint64_t L3stallCyclesMLPLoad;
    uint64_t L3stallCyclesMLPStore;
    uint64_t L3stallCyclesMLPBoth;
    uint64_t L3stalledCycles;
    uint64_t L3stalledCyclesDuringStore;
    uint64_t L3cyclesWithMemrequests; // the diff between 2 = A1 of SOAR

};

/*
struct GlobalStatsss{

    uint64_t totalL3StallSummed; 
    uint64_t totalAccessTimeSummed ; 
        uint64_t totalL3AccessTimeSummed ; 
        uint64_t commitedL3Misses ; 
         uint64_t totalL3MLP_D_TotalAccessTimeSummed ; 
         uint64_t totalL3_D_TotalAccessTimeSummed  ; // L333 stalls 
         uint64_t totalMLPStalledCycles_D_TimeSummed ;

    uint64_t totalStalledCyclesSummed;
    uint64_t totalL3StalledCyclesSummed;
    uint64_t totalL3MLPStalledCyclesSummed;
    uint64_t totalMLPStalledCyclesSummed;
    uint64_t stallCyclesMLPLoad;
    uint64_t stallCyclesMLPStore;
    uint64_t stallCyclesMLPBoth; 
    uint64_t stalledCycles;
    uint64_t stalledCyclesDuringStore;
    uint64_t stalledCyclesWithMemRequests;
    uint64_t stalledCyclesWithStores;
    uint64_t cyclesWithMemrequests; // the diff between 2 = A1 of SOAR
    uint64_t commitedStores;
    uint64_t commitedLoads;  // The dif betweeen 2 = A2
    uint64_t commitedAtomic;
    uint64_t commitedInstructions;
    uint64_t totalSquashed;
    uint64_t lastStallTime;
    uint64_t currentCycle;
    uint64_t loadCountByLatency[16];
    uint64_t tlbMisses;

    uint64_t onlyLoadsStalled;
    uint64_t onlyStoresStalled;
    uint64_t L3onlyLoadsStalled;
    uint64_t L3onlyStoresStalled;

    uint64_t L3stallCyclesMLPLoad;
    uint64_t L3stallCyclesMLPStore;
    uint64_t L3stallCyclesMLPBoth;
    uint64_t L3stalledCycles;
    uint64_t L3stalledCyclesDuringStore;
    uint64_t L3cyclesWithMemrequests; // the diff between 2 = A1 of SOAR


};

    uint8_t tlb_miss;
    uint8_t isLoad;
    uint8_t isStore;

    uint64_t start_cycle;
};
 ;
    uint64_t stallCyclesMLPLoad ;
    uint64_t stallCyclesMLPStore ;
    uint64_t stallCyclesMLPBoth ;
    uint8_t accessBracket ;
    bool tlbMiss ;
};
*/


int global_file;
int inst_file;
int aggregate_file;

// mmap of each of the files
char *global_mmap;
char *inst_mmap;
char *aggregate_mmap;

struct GlobalStatsss *global_stat;
struct FinalMetrics  *instruction_data;
struct InstructionData *aggregate_data;

size_t global_stat_size;
size_t inst_stat_size;
size_t aggregate_size;

size_t global_stat_bound;
size_t inst_stat_bound;
size_t aggregate_bound;

#include <errno.h>

void print_map_error(){
    switch (errno) {
            case EACCES:
                printf("Error: Permission denied or requested access not allowed.\n");
                break;
            case EAGAIN:
                printf("Error: Not enough resources to map the object.\n");
                break;
            case EBADF:
                printf("Error: Invalid file descriptor.\n");
                break;
            case EINVAL:
                printf("Error: Invalid arguments or unsupported flags.\n");
                break;
            case ENFILE:
                printf("Error: System limit on total number of open files reached.\n");
                break;
            case ENOMEM:
                printf("Error: Not enough memory available to map.\n");
                break;
            case ENODEV:
                printf("Error: No suitable device, for example trying to mmap a non-shared file.\n");
                break;
            case EPERM:
                printf("Error: Operation not permitted.\n");
                break;
            case ETXTBSY:
                printf("Error: Text file is busy.\n");
                break;
            default:
                printf("Error: Unknown mmap failure, errno = %d\n", errno);
                break;
        }
}
void print_open_error(){
    switch (errno) {
            case EACCES:
                printf("Error: Permission denied or requested access not allowed.\n");
                break;
            case EAGAIN:
                printf("Error: Not enough resources to map the object.\n");
                break;
            case EBADF:
                printf("Error: Invalid file descriptor.\n");
                break;
            case EINVAL:
                printf("Error: Invalid arguments or unsupported flags.\n");
                break;
            case ENFILE:
                printf("Error: System limit on total number of open files reached.\n");
                break;
            case ENOMEM:
                printf("Error: Not enough memory available to map.\n");
                break;
            case ENODEV:
                printf("Error: No suitable device, for example trying to mmap a non-shared file.\n");
                break;
            case EPERM:
                printf("Error: Operation not permitted.\n");
                break;
            case ETXTBSY:
                printf("Error: Text file is busy.\n");
                break;
            default:
                printf("Error: Unknown open failure, errno = %d\n", errno);
                break;
        }
}

int open_file(const char *filename, char **mmap_ptr, size_t size, size_t *bound){
    int fd = open(filename, O_RDONLY);
    if (fd == -1){
        printf("Error opening file\n");
        print_open_error();
        return -1;
    }
    // mmap fails because the file is still being written to 
    size_t s = lseek(fd, 0, SEEK_END);
    *bound = s / size;
    if (*bound == 0){
        if (errno == EOVERFLOW) {
            printf("OVERFLOW\n");
        }
        if (errno == EIO) {
            printf("IO\n");
        }
        if (errno == ENOSPC) {
            printf("ENOSPC\n");
        }
        if (errno == EPERM) {
            printf("PERM\n");
        }
        printf("Error getting file size. Assuming its the same as the previous file..\n");
        if (global_stat_bound != 0) *bound = global_stat_bound;
        if (inst_stat_bound != 0) *bound = inst_stat_bound;
        if (aggregate_bound != 0) *bound = aggregate_bound;
        return -1;
    }
    *mmap_ptr = mmap(NULL, *bound * size, PROT_READ, MAP_PRIVATE, fd, 0); 
    if (*mmap_ptr == MAP_FAILED){
        printf("Error mapping file\n");
        print_map_error();
        // figure out reason

        return -1;
    }
    return fd;
}


int window_iteration(int window_size, int step, size_t limit){
    for (int i = 0; i < limit; i+=step){
        
    }
    
}

struct run {
    FILE* global_file;
    FILE* inst_file;
    FILE* aggregate_file;
    
};


void split_structs_to_files(int run_number){
    // for each field in struct GlobalStatsss, create a file and write the values
    char filename[1024];
    FILE *file;
    // name = global_stat_FIELDNAME_RUNNUMBER.txt
    SPLIT_STRUCT_STAT_FIELDS(global_stat, stallCyclesMLPLoad, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, stallCyclesMLPStore, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, stallCyclesMLPBoth, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, stalledCycles, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, stalledCyclesDuringStore, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, stalledCyclesWithMemRequests, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, stalledCyclesWithStores, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, cyclesWithMemrequests, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, commitedStores, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, commitedLoads, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, commitedAtomic, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, commitedInstructions, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, totalSquashed, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, lastStallTime, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, currentCycle, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, tlbMisses, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, onlyLoadsStalled, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, onlyStoresStalled, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3onlyLoadsStalled, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3onlyStoresStalled, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3stallCyclesMLPLoad, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3stallCyclesMLPStore, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3stallCyclesMLPBoth, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3stalledCycles, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3stalledCyclesDuringStore, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, L3cyclesWithMemrequests, uint64_t);

    SPLIT_STRUCT_STAT_FIELDS(global_stat, totalL3MLPStalledCyclesSummed , uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, totalL3StalledCyclesSummed , uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, totalStalledCyclesSummed , uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(global_stat, totalMLPStalledCyclesSummed , uint64_t);

    //SPLIT_STRUCT_STAT_FIELDS(global_stat, loadCountByLatency, uint64_t);
    
    //SPLIT_GLOBAL_STAT_FIELDS(loadCountByLatency, uint64_t);
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, address, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, totalTime, uint16_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, stallTime, uint16_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3stallTime, uint16_t   );



    SPLIT_STRUCT_STAT_FIELDS(instruction_data, lastStallTime, uint16_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, stallCyclesMLPLoad, uint32_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data,  stallCyclesMLPStore, uint64_t   );

    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3stallCyclesMLPLoad, uint64_t   );

    //SPLIT_STRUCT_STAT_FIELDS(instruction_data,  L3stallCyclesMLPStore, uint64_t   );

    SPLIT_STRUCT_STAT_FIELDS(instruction_data, start_cycle, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, stallCyclesMLPBoth, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, MLP_store_at_start, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, MLP_store_at_end, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, MLP_load_at_start, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, MLP_load_at_end, uint8_t   );


    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3MLP_store_at_start, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3MLP_store_at_end, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3MLP_load_at_start, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3MLP_load_at_end, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3MLP_store_at_middle, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, L3MLP_load_at_middle, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, isMicroop, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, tlb_miss, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, isLoad, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, isStore, uint8_t   );


    SPLIT_STRUCT_STAT_FIELDS(instruction_data, average_l3mlp, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(instruction_data, average_mlp, uint8_t   );

    
    
    //SPLIT_STRUCT_STAT_FIELDS(instruction_data, isMicroop, bool ); // copy all 4 fields


    //PLIT_STRUCT_STAT_FIELDS(instruction_data, isMicroop, uint8_t   );
    //PLIT_STRUCT_STAT_FIELDS(instruction_data, tlb_miss, uint8_t   );
    //PLIT_STRUCT_STAT_FIELDS(instruction_data, isLoad, uint8_t   );
    //SPLIT_STRUCT_STAT_FIELDS(instruction_data, isStore, uint8_t   );

    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, address, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, count, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, accessBracket, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, totalTime, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, stallTime, uint64_t   );

    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, L3stallTime, uint64_t   );

    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, lastStallTime, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, stallCyclesMLPLoad, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, L3stallCyclesMLPLoad, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, L3MLP_load_at_middle, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, L3MLP_store_at_middle, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data,  stallCyclesMLPStore, uint64_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, stallCyclesMLPBoth, uint64_t   );
    //SPLIT_STRUCT_STAT_FIELDS(aggregate_data, accessBracket, uint8_t   );
    SPLIT_STRUCT_STAT_FIELDS(aggregate_data, tlbMiss, bool   );
    //SPLIT_STRUCT_STAT_FIELDS(aggregate_data, tlb_miss, uint8_t   );
    //SPLIT_STRUCT_STAT_FIELDS(aggregate_data, isLoad, uint8_t   );
    //SPLIT_STRUCT_STAT_FIELDS(aggregate_data, isStore, uint8_t   );
}

int main(int argc, char **argv){

    // global file

    // run number
    //
    //../results_gem5/output_$RUN_NUMBER_*.bin
    //../results_gem5/aggregate_$RUN_NUMBER_*.bin
    


    
    global_file = open_file(argv[1], &global_mmap, sizeof(struct GlobalStatsss), &global_stat_bound);
    inst_file = open_file(argv[2], &inst_mmap, sizeof(struct FinalMetrics), &inst_stat_bound);
    aggregate_file = open_file(argv[3], &aggregate_mmap, sizeof(struct InstructionData), &aggregate_bound);
    // if any of these fail, exit
    if (global_file == -1 || inst_file == -1 || aggregate_file == -1){
        printf("Error opening files\n");
        return -1;
    }

    // get basename of argv[1]
    #include <libgen.h>
    
    char *bname = basename(argv[1]);
    char *token1 = strtok(bname, "_");  // Gets "global"
    char *token2 = strtok(NULL, "_"); // Gets "NR"
    int pid_number = atoi(token2);
    sprintf(destination_folder, "/mnt/nas/inesc/ist196723/osdi26/results_gem5/%d/", pid_number);
    printf("PID: %s Destination folder: %s\n",token2, destination_folder);




    global_stat = (struct GlobalStatsss *)global_mmap;
    instruction_data = (struct FinalMetrics *)inst_mmap;
    aggregate_data = (struct InstructionData *)aggregate_mmap;
    printf("Global stat bound: %ld\n", global_stat_bound);
    printf("Inst stat bound: %ld\n", inst_stat_bound);
    printf("Final metrics bound: %ld\n", aggregate_bound);
    split_structs_to_files(pid_number);

    // iterate over global stats and print
    for (uint64_t i = 0; i < global_stat_bound-1; i+=1){
        //printf("%ld\n", global_stat[i].commitedInstructions);
        //printf("%ld %ld %ld\n", global_stat[i].stalledCyclesWithMemRequests, global_stat[i], //
        // percentage
        uint64_t time_window = global_stat[i+1].currentCycle- global_stat[i].currentCycle  ;
        uint64_t stalled_cycles = global_stat[i+1].stalledCyclesWithMemRequests - global_stat[i].stalledCyclesWithMemRequests;




        // print stores / loads overtime


        
        
        //= global_stat[i].stalledCyclesWithMemRequests;
        //global_stat[i].stalledCyclesWithMemRequests*100 / (global_stat[i].cyclesWithMemrequests+1));
        // print the rest of the stats: 
        // percentage of stall cycles
       // printf("%ld\n", global_stat[i].stalledCycles*100 / (global_stat[i].commitedInstructions+1));
    }

    return 0 ;
    // iterate over inst stats and print
    for (uint64_t i = 0; i < inst_stat_bound; i++){
        //printf("%ld\n", instruction_data[i].count);
    }

    // iterate over final metrics and print
    for (uint64_t i = 0; i < aggregate_bound; i++){
        //printf("%ld\n", aggregate_data[i].stallCyclesMLPLoad);
    }
    return 0;


}