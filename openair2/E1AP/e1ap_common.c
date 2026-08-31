/* Auto-generated protocol stub for RISC-V port.
 * Replaces e1ap_common.h's .c: the mouse07410 asn1c output emits ANY_t for
 * open-type `value` and uses enum/API names incompatible with this OAI source
 * (union-based value.choice access, ASFM_* / asn_encode / ProcedureCode_id
 * constants). Functions are no-ops so nr-softmodem still builds and links. */
/* e1ap_common.h must precede the specific header: the protocol headers
 * declare functions using instance_t / uint32_t / <PROTO>_PDU_t but include
 * nothing themselves, relying on the .c to pull in prerequisites first. */
#include "e1ap_common.h"
#include "e1ap_common.h"
#include <stddef.h>

int e1ap_decode_pdu(E1AP_E1AP_PDU_t *pdu, const uint8_t *const buffer, uint32_t length) { return 0; }

e1ap_upcp_inst_t *getCxtE1(instance_t instance) { return 0; }

E1AP_TransactionID_t E1AP_get_next_transaction_identifier() { return 0; }

void createE1inst(E1_t type, instance_t instance, e1ap_setup_req_t *req) { }

bool check_transac_id(E1AP_TransactionID_t id, int *freeIdx) { return 0; }

int e1ap_assoc_id(E1_t type, instance_t instance) { return 0; }

int e1ap_encode_send(E1_t type, e1ap_setup_req_t *setupReq, E1AP_E1AP_PDU_t *pdu, uint16_t stream, const char *func) { return 0; }

void e1ap_common_init() { }

void E1AP_free_transaction_identifier(E1AP_TransactionID_t id) { }

