/* Auto-generated NGAP OAI compatibility header */
#ifndef NGAP_OAI_COMPAT_H
#define NGAP_OAI_COMPAT_H

#include "constr_TYPE.h"
#include <asn_application.h>
#include <ANY.h>
#include "OCTET_STRING.h"
#include "NGAP_ProcedureCode.h"
#include "NGAP_Criticality.h"
#include "NGAP_ProtocolIE-ID.h"

#include "NGAP_Cause.h"
#include "NGAP_GlobalRANNodeID.h"
#include "NGAP_SupportedTAList.h"
#include "NGAP_ServedGUAMIList.h"
#include "NGAP_PLMNSupportList.h"
#include "NGAP_UEAggregateMaximumBitRate.h"
#include "NGAP_GUAMI.h"
#include "NGAP_AllowedNSSAI.h"
#include "NGAP_UESecurityCapabilities.h"
#include "NGAP_MobilityRestrictionList.h"
#include "NGAP_UserLocationInformation.h"
#include "NGAP_UEPagingIdentity.h"
#include "NGAP_TAIListForPaging.h"
#include "NGAP_TAI.h"
#include "NGAP_BroadcastPLMNItem.h"
#include "NGAP_SliceSupportItem.h"
#include "NGAP_PLMNIdentity.h"
#include "NGAP_TAC.h"
#include "NGAP_SD.h"
#include "NGAP_PDUSessionResourceListCxtRelReq.h"
#include "NGAP_FiveG-S-TMSI.h"
#include "NGAP_UE-NGAP-IDs.h"
#include "NGAP_UEContextReleaseRequest.h"
#include "NGAP_NGSetupRequest.h"
#include "NGAP_NGSetupResponse.h"
#include "NGAP_ErrorIndication.h"
#include "NGAP_InitialContextSetupRequest.h"
#include "NGAP_InitialContextSetupResponse.h"
#include "NGAP_UEContextReleaseCommand.h"
#include "NGAP_UEContextReleaseComplete.h"
#include "NGAP_PDUSessionResourceSetupRequest.h"
#include "NGAP_PDUSessionResourceSetupResponse.h"
#include "NGAP_PDUSessionResourceModifyRequest.h"
#include "NGAP_PDUSessionResourceModifyResponse.h"
#include "NGAP_PDUSessionResourceReleaseCommand.h"
#include "NGAP_PDUSessionResourceReleaseResponse.h"
#include "NGAP_InitialUEMessage.h"
#include "NGAP_DownlinkNASTransport.h"
#include "NGAP_UplinkNASTransport.h"
#include "NGAP_Paging.h"
#include "NGAP_PathSwitchRequest.h"
#include "NGAP_OverloadStart.h"
#include "NGAP_OverloadStop.h"
#include "NGAP_NGAP-PDU.h"

#include "NGAP_PDUSessionResourceSetupListCxtReq.h"
#include "NGAP_PDUSessionResourceSetupListCxtRes.h"
#include "NGAP_PDUSessionResourceFailedToSetupListCxtRes.h"
#include "NGAP_PDUSessionResourceSetupListSUReq.h"
#include "NGAP_PDUSessionResourceSetupListSURes.h"
#include "NGAP_PDUSessionResourceFailedToSetupListSURes.h"
#include "NGAP_PDUSessionResourceModifyListModReq.h"
#include "NGAP_PDUSessionResourceModifyListModRes.h"
#include "NGAP_PDUSessionResourceFailedToModifyListModRes.h"
#include "NGAP_PDUSessionResourceReleasedListRelRes.h"
#include "NGAP_PDUSessionResourceToReleaseListRelCmd.h"
#include "NGAP_CriticalityDiagnostics.h"
#include "NGAP_AMFName.h"
#include "NGAP_RANNodeName.h"
#include "NGAP_SecurityKey.h"
#include "NGAP_UERadioCapability.h"
#include "NGAP_RelativeAMFCapacity.h"
#include "NGAP_PagingDRX.h"
#include "NGAP_RRCEstablishmentCause.h"
#include "NGAP_UEContextRequest.h"
#include "NGAP_NGSetupFailure.h"
#include "NGAP_InitialContextSetupFailure.h"
#include "NGAP_UEContextModificationRequest.h"
#include "NGAP_UEContextModificationResponse.h"
#include "NGAP_UEContextModificationFailure.h"
#include "NGAP_PDUSessionResourceModifyIndication.h"
#include "NGAP_PDUSessionResourceNotify.h"
#include "NGAP_NASNonDeliveryIndication.h"
#include "NGAP_UERadioCapabilityInfoIndication.h"

#ifdef __cplusplus
extern "C" {
#endif

/* NGAP ProcedureCode IDs */
#define NGAP_ProcedureCode_id_DownlinkNASTransport 4
#define NGAP_ProcedureCode_id_ErrorIndication 9
#define NGAP_ProcedureCode_id_InitialContextSetup 14
#define NGAP_ProcedureCode_id_InitialUEMessage 15
#define NGAP_ProcedureCode_id_NASNonDeliveryIndication 19
#define NGAP_ProcedureCode_id_NGSetup 21
#define NGAP_ProcedureCode_id_OverloadStart 22
#define NGAP_ProcedureCode_id_OverloadStop 23
#define NGAP_ProcedureCode_id_PDUSessionResourceModify 26
#define NGAP_ProcedureCode_id_PDUSessionResourceModifyIndication 27
#define NGAP_ProcedureCode_id_PDUSessionResourceNotify 30
#define NGAP_ProcedureCode_id_PDUSessionResourceRelease 28
#define NGAP_ProcedureCode_id_PDUSessionResourceSetup 29
#define NGAP_ProcedureCode_id_Paging 24
#define NGAP_ProcedureCode_id_PathSwitchRequest 25
#define NGAP_ProcedureCode_id_UEContextModification 40
#define NGAP_ProcedureCode_id_UEContextRelease 41
#define NGAP_ProcedureCode_id_UERadioCapabilityInfoIndication 44
#define NGAP_ProcedureCode_id_UplinkNASTransport 46

#define NGAP_ProcedureCode_id_UEContextReleaseRequest 42
/* NGAP ProtocolIE-ID constants */
#define NGAP_ProtocolIE_id_AMFName 1
#define NGAP_ProtocolIE_ID_id_AMFName 1
#define NGAP_ProtocolIE_id_AMF_UE_NGAP_ID 10
#define NGAP_ProtocolIE_ID_id_AMF_UE_NGAP_ID 10
#define NGAP_ProtocolIE_id_AllowedNSSAI 0
#define NGAP_ProtocolIE_ID_id_AllowedNSSAI 0
#define NGAP_ProtocolIE_id_Cause 15
#define NGAP_ProtocolIE_ID_id_Cause 15
#define NGAP_ProtocolIE_id_CriticalityDiagnostics 19
#define NGAP_ProtocolIE_ID_id_CriticalityDiagnostics 19
#define NGAP_ProtocolIE_id_DefaultPagingDRX 21
#define NGAP_ProtocolIE_ID_id_DefaultPagingDRX 21
#define NGAP_ProtocolIE_id_FiveG_S_TMSI 26
#define NGAP_ProtocolIE_ID_id_FiveG_S_TMSI 26
#define NGAP_ProtocolIE_id_GUAMI 28
#define NGAP_ProtocolIE_ID_id_GUAMI 28
#define NGAP_ProtocolIE_id_GlobalRANNodeID 27
#define NGAP_ProtocolIE_ID_id_GlobalRANNodeID 27
#define NGAP_ProtocolIE_id_MobilityRestrictionList 36
#define NGAP_ProtocolIE_ID_id_MobilityRestrictionList 36
#define NGAP_ProtocolIE_id_NAS_PDU 38
#define NGAP_ProtocolIE_ID_id_NAS_PDU 38
#define NGAP_ProtocolIE_id_PDUSessionResourceFailedToModifyListModRes 57
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceFailedToModifyListModRes 57
#define NGAP_ProtocolIE_id_PDUSessionResourceFailedToSetupListCxtRes 55
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceFailedToSetupListCxtRes 55
#define NGAP_ProtocolIE_id_PDUSessionResourceFailedToSetupListSURes 58
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceFailedToSetupListSURes 58
#define NGAP_ProtocolIE_id_PDUSessionResourceListCxtRelCmd 117
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceListCxtRelCmd 117
#define NGAP_ProtocolIE_id_PDUSessionResourceListCxtRelReq 116
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceListCxtRelReq 116
#define NGAP_ProtocolIE_id_PDUSessionResourceModifyListModInd 63
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceModifyListModInd 63
#define NGAP_ProtocolIE_id_PDUSessionResourceModifyListModReq 64
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceModifyListModReq 64
#define NGAP_ProtocolIE_id_PDUSessionResourceModifyListModRes 65
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceModifyListModRes 65
#define NGAP_ProtocolIE_id_PDUSessionResourceNotifyList 62
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceNotifyList 62
#define NGAP_ProtocolIE_id_PDUSessionResourceReleasedListRelCmd 69
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceReleasedListRelCmd 69
#define NGAP_ProtocolIE_id_PDUSessionResourceReleasedListRelReq 68
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceReleasedListRelReq 68
#define NGAP_ProtocolIE_id_PDUSessionResourceReleasedListRelRes 70
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceReleasedListRelRes 70
#define NGAP_ProtocolIE_id_PDUSessionResourceSetupListCxtReq 71
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceSetupListCxtReq 71
#define NGAP_ProtocolIE_id_PDUSessionResourceSetupListCxtRes 72
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceSetupListCxtRes 72
#define NGAP_ProtocolIE_id_PDUSessionResourceSetupListSUReq 74
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceSetupListSUReq 74
#define NGAP_ProtocolIE_id_PDUSessionResourceSetupListSURes 75
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceSetupListSURes 75
#define NGAP_ProtocolIE_id_PDUSessionResourceSetupUnsuccessfulTransfer 77
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceSetupUnsuccessfulTransfer 77
#define NGAP_ProtocolIE_id_PDUSessionResourceToReleaseListRelCmd 79
#define NGAP_ProtocolIE_ID_id_PDUSessionResourceToReleaseListRelCmd 79
#define NGAP_ProtocolIE_id_PLMNSupportList 80
#define NGAP_ProtocolIE_ID_id_PLMNSupportList 80
#define NGAP_ProtocolIE_id_PagingDRX 50
#define NGAP_ProtocolIE_ID_id_PagingDRX 50
#define NGAP_ProtocolIE_id_RANNodeName 82
#define NGAP_ProtocolIE_ID_id_RANNodeName 82
#define NGAP_ProtocolIE_id_RAN_UE_NGAP_ID 85
#define NGAP_ProtocolIE_ID_id_RAN_UE_NGAP_ID 85
#define NGAP_ProtocolIE_id_RRCEstablishmentCause 90
#define NGAP_ProtocolIE_ID_id_RRCEstablishmentCause 90
#define NGAP_ProtocolIE_id_RelativeAMFCapacity 86
#define NGAP_ProtocolIE_ID_id_RelativeAMFCapacity 86
#define NGAP_ProtocolIE_id_SecurityKey 94
#define NGAP_ProtocolIE_ID_id_SecurityKey 94
#define NGAP_ProtocolIE_id_ServedGUAMIList 96
#define NGAP_ProtocolIE_ID_id_ServedGUAMIList 96
#define NGAP_ProtocolIE_id_SupportedTAList 112
#define NGAP_ProtocolIE_ID_id_SupportedTAList 112
#define NGAP_ProtocolIE_id_TAIListForPaging 111
#define NGAP_ProtocolIE_ID_id_TAIListForPaging 111
#define NGAP_ProtocolIE_id_UEAggregateMaximumBitRate 104
#define NGAP_ProtocolIE_ID_id_UEAggregateMaximumBitRate 104
#define NGAP_ProtocolIE_id_UEContextRequest 114
#define NGAP_ProtocolIE_ID_id_UEContextRequest 114
#define NGAP_ProtocolIE_id_UEPagingIdentity 110
#define NGAP_ProtocolIE_ID_id_UEPagingIdentity 110
#define NGAP_ProtocolIE_id_UERadioCapability 115
#define NGAP_ProtocolIE_ID_id_UERadioCapability 115
#define NGAP_ProtocolIE_id_UESecurityCapabilities 107
#define NGAP_ProtocolIE_ID_id_UESecurityCapabilities 107
#define NGAP_ProtocolIE_id_UE_NGAP_IDs 109
#define NGAP_ProtocolIE_ID_id_UE_NGAP_IDs 109
#define NGAP_ProtocolIE_id_UserLocationInformation 113
#define NGAP_ProtocolIE_ID_id_UserLocationInformation 113

/* IE value with comprehensive pointer union */
typedef struct NGAP_IE_Value {
    long present;  /* discriminator */
    union NGAP_IE_Value_u {
        void *ptr;
        /* Compound types with headers */
        struct NGAP_GlobalRANNodeID *GlobalRANNodeID;
        struct NGAP_SupportedTAList *SupportedTAList;
        struct NGAP_Cause *Cause;
        struct NGAP_ServedGUAMIList *ServedGUAMIList;
        struct NGAP_PLMNSupportList *PLMNSupportList;
        struct NGAP_UEAggregateMaximumBitRate *UEAggregateMaximumBitRate;
        struct NGAP_GUAMI *GUAMI;
        struct NGAP_AllowedNSSAI *AllowedNSSAI;
        struct NGAP_UESecurityCapabilities *UESecurityCapabilities;
        struct NGAP_MobilityRestrictionList *MobilityRestrictionList;
        struct NGAP_UserLocationInformation *UserLocationInformation;
        struct NGAP_UEPagingIdentity *UEPagingIdentity;
        struct NGAP_TAIListForPaging *TAIListForPaging;
        struct NGAP_PDUSessionResourceSetupListCxtReq *PDUSessionResourceSetupListCxtReq;
        struct NGAP_PDUSessionResourceSetupListCxtRes *PDUSessionResourceSetupListCxtRes;
        struct NGAP_PDUSessionResourceFailedToSetupListCxtRes *PDUSessionResourceFailedToSetupListCxtRes;
        struct NGAP_PDUSessionResourceSetupListSUReq *PDUSessionResourceSetupListSUReq;
        struct NGAP_PDUSessionResourceSetupListSURes *PDUSessionResourceSetupListSURes;
        struct NGAP_PDUSessionResourceFailedToSetupListSURes *PDUSessionResourceFailedToSetupListSURes;
        struct NGAP_PDUSessionResourceModifyListModReq *PDUSessionResourceModifyListModReq;
        struct NGAP_PDUSessionResourceModifyListModRes *PDUSessionResourceModifyListModRes;
        struct NGAP_PDUSessionResourceFailedToModifyListModRes *PDUSessionResourceFailedToModifyListModRes;
        struct NGAP_PDUSessionResourceReleasedListRelRes *PDUSessionResourceReleasedListRelRes;
        struct NGAP_PDUSessionResourceToReleaseListRelCmd *PDUSessionResourceToReleaseListRelCmd;
        struct NGAP_CriticalityDiagnostics *CriticalityDiagnostics;
        /* Embedded types - OAI accesses these with . (by value) */
        NGAP_PDUSessionResourceListCxtRelReq_t PDUSessionResourceListCxtRelReq;
        NGAP_FiveG_S_TMSI_t FiveG_S_TMSI;
        NGAP_UE_NGAP_IDs_t UE_NGAP_IDs;
        /* Simple/scalar types - embedded, not pointers (OAI uses them by value) */
        OCTET_STRING_t RANNodeName;       /* PrintableString_t */
        OCTET_STRING_t AMFName;            /* PrintableString_t */
        OCTET_STRING_t NAS_PDU;            /* OCTET_STRING_t */
        OCTET_STRING_t SecurityKey;        /* BIT_STRING_t */
        OCTET_STRING_t UERadioCapability;  /* OCTET_STRING_t */
        long AMF_UE_NGAP_ID;
        long RAN_UE_NGAP_ID;
        long RelativeAMFCapacity;
        long PagingDRX;
        long DefaultPagingDRX;
        long RRCEstablishmentCause;
        long UEContextRequest;
    } choice;
} NGAP_IE_Value_t;

/* Generic IE structure - this is the complete definition of
 * struct NGAP_ProtocolIE_Field referenced by generated containers
 * (NGAP_ProtocolIE_Container_*) via A_SEQUENCE_OF(struct NGAP_ProtocolIE_Field).
 * The generated code only forward-declares it; we define it here so that
 * OAI's NGAP_FIND_PROTOCOLIE_BY_ID macro can dereference list.array elements. */
struct NGAP_ProtocolIE_Field {
    NGAP_ProtocolIE_ID_t     id;
    NGAP_Criticality_t       criticality;
    NGAP_IE_Value_t  value;
    asn_struct_ctx_t _asn_ctx;
};
typedef struct NGAP_ProtocolIE_Field NGAP_ProtocolIE_Field_t;
typedef struct NGAP_ProtocolIE_Field NGAP_Message_IEs_t;

typedef NGAP_Message_IEs_t NGAP_NGSetupRequestIEs_t;
typedef NGAP_Message_IEs_t NGAP_NGSetupResponseIEs_t;
typedef NGAP_Message_IEs_t NGAP_NGSetupFailureIEs_t;
typedef NGAP_Message_IEs_t NGAP_ErrorIndicationIEs_t;
typedef NGAP_Message_IEs_t NGAP_InitialContextSetupRequestIEs_t;
typedef NGAP_Message_IEs_t NGAP_InitialContextSetupResponseIEs_t;
typedef NGAP_Message_IEs_t NGAP_InitialContextSetupFailureIEs_t;
typedef NGAP_Message_IEs_t NGAP_UEContextReleaseCommand_IEs_t;
typedef NGAP_Message_IEs_t NGAP_UEContextReleaseComplete_IEs_t;
typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceSetupRequestIEs_t;
typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceSetupResponseIEs_t;
typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceModifyRequestIEs_t;
typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceModifyResponseIEs_t;
typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceReleaseCommandIEs_t;
typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceReleaseResponseIEs_t;
typedef NGAP_Message_IEs_t NGAP_InitialUEMessage_IEs_t;
typedef NGAP_Message_IEs_t NGAP_DownlinkNASTransport_IEs_t;
typedef NGAP_Message_IEs_t NGAP_UplinkNASTransport_IEs_t;
typedef NGAP_Message_IEs_t NGAP_NASNonDeliveryIndication_IEs_t;
typedef NGAP_Message_IEs_t NGAP_UERadioCapabilityInfoIndicationIEs_t;
typedef NGAP_Message_IEs_t NGAP_PagingIEs_t;
typedef NGAP_Message_IEs_t NGAP_PathSwitchRequestIEs_t;
typedef NGAP_Message_IEs_t NGAP_OverloadStartIEs_t;
typedef NGAP_Message_IEs_t NGAP_OverloadStopIEs_t;
typedef NGAP_Message_IEs_t NGAP_UEContextModificationRequestIEs_t;
typedef NGAP_Message_IEs_t NGAP_UEContextModificationResponseIEs_t;
typedef NGAP_Message_IEs_t NGAP_PDUSessionResourceNotifyIEs_t;
typedef NGAP_Message_IEs_t NGAP_DeactivateTraceIEs_t;
typedef NGAP_Message_IEs_t NGAP_UEContextReleaseRequest_IEs_t;

/* IE value PR enum values */
#define NGAP_NGSetupRequestIEs__value_PR_GlobalRANNodeID 0
#define NGAP_NGSetupRequestIEs__value_PR_RANNodeName 1
#define NGAP_NGSetupRequestIEs__value_PR_SupportedTAList 2
#define NGAP_NGSetupRequestIEs__value_PR_DefaultPagingDRX 3
#define NGAP_NGSetupResponseIEs__value_PR_Cause 0
#define NGAP_NGSetupResponseIEs__value_PR_ServedGUAMIList 1
#define NGAP_NGSetupResponseIEs__value_PR_RelativeAMFCapacity 2
#define NGAP_NGSetupResponseIEs__value_PR_AMFName 3
#define NGAP_NGSetupResponseIEs__value_PR_PLMNSupportList 4
#define NGAP_NGSetupResponseIEs__value_PR_CriticalityDiagnostics 5
#define NGAP_NGSetupFailureIEs__value_PR_Cause 0
#define NGAP_NGSetupFailureIEs__value_PR_CriticalityDiagnostics 1
#define NGAP_ErrorIndicationIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_ErrorIndicationIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_ErrorIndicationIEs__value_PR_Cause 2
#define NGAP_ErrorIndicationIEs__value_PR_CriticalityDiagnostics 3
#define NGAP_InitialContextSetupRequestIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_InitialContextSetupRequestIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_InitialContextSetupRequestIEs__value_PR_UEAggregateMaximumBitRate 2
#define NGAP_InitialContextSetupRequestIEs__value_PR_GUAMI 3
#define NGAP_InitialContextSetupRequestIEs__value_PR_PDUSessionResourceSetupListCxtReq 4
#define NGAP_InitialContextSetupRequestIEs__value_PR_AllowedNSSAI 5
#define NGAP_InitialContextSetupRequestIEs__value_PR_UESecurityCapabilities 6
#define NGAP_InitialContextSetupRequestIEs__value_PR_SecurityKey 7
#define NGAP_InitialContextSetupRequestIEs__value_PR_MobilityRestrictionList 8
#define NGAP_InitialContextSetupRequestIEs__value_PR_NAS_PDU 9
#define NGAP_InitialContextSetupResponseIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_InitialContextSetupResponseIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_InitialContextSetupResponseIEs__value_PR_PDUSessionResourceSetupListCxtRes 2
#define NGAP_InitialContextSetupResponseIEs__value_PR_PDUSessionResourceFailedToSetupListCxtRes 3
#define NGAP_InitialContextSetupResponseIEs__value_PR_CriticalityDiagnostics 4
#define NGAP_PDUSessionResourceSetupRequestIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceSetupRequestIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PDUSessionResourceSetupRequestIEs__value_PR_UEAggregateMaximumBitRate 2
#define NGAP_PDUSessionResourceSetupRequestIEs__value_PR_PDUSessionResourceSetupListSUReq 3
#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_PDUSessionResourceSetupListSURes 2
#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_PDUSessionResourceFailedToSetupListSURes 3
#define NGAP_PDUSessionResourceSetupResponseIEs__value_PR_CriticalityDiagnostics 4
#define NGAP_UEContextReleaseCommand_IEs__value_PR_UE_NGAP_IDs 0
#define NGAP_UEContextReleaseCommand_IEs__value_PR_Cause 1
#define NGAP_PagingIEs__value_PR_UEPagingIdentity 0
#define NGAP_PagingIEs__value_PR_PagingDRX 1
#define NGAP_PagingIEs__value_PR_TAIListForPaging 2
#define NGAP_InitialUEMessage_IEs__value_PR_RAN_UE_NGAP_ID 0
#define NGAP_InitialUEMessage_IEs__value_PR_NAS_PDU 1
#define NGAP_InitialUEMessage_IEs__value_PR_UserLocationInformation 2
#define NGAP_InitialUEMessage_IEs__value_PR_RRCEstablishmentCause 3
#define NGAP_DownlinkNASTransport_IEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_DownlinkNASTransport_IEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_DownlinkNASTransport_IEs__value_PR_NAS_PDU 2
#define NGAP_UplinkNASTransport_IEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_UplinkNASTransport_IEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_UplinkNASTransport_IEs__value_PR_NAS_PDU 2
#define NGAP_UplinkNASTransport_IEs__value_PR_UserLocationInformation 3
#define NGAP_PathSwitchRequestIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PathSwitchRequestIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PathSwitchRequestIEs__value_PR_Cause 2
#define NGAP_PathSwitchRequestIEs__value_PR_PDUSessionResourceToReleaseListRelCmd 3

#define NGAP_NGSetupRequestIEs__value_PR_PagingDRX 3
#define NGAP_UEContextReleaseComplete_IEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_UEContextReleaseComplete_IEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_UEContextReleaseComplete_IEs__value_PR_PDUSessionResourceListCxtRelReq 2
#define NGAP_UEContextReleaseComplete_IEs__value_PR_Cause 3
#define NGAP_UEContextReleaseRequest_IEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_UEContextReleaseRequest_IEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_UEContextReleaseRequest_IEs__value_PR_PDUSessionResourceListCxtRelReq 2
#define NGAP_UEContextReleaseRequest_IEs__value_PR_Cause 3
#define NGAP_PDUSessionResourceModifyRequestIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceModifyRequestIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PDUSessionResourceModifyRequestIEs__value_PR_PDUSessionResourceModifyListModReq 2
#define NGAP_PDUSessionResourceModifyResponseIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceModifyResponseIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PDUSessionResourceModifyResponseIEs__value_PR_PDUSessionResourceModifyListModRes 2
#define NGAP_PDUSessionResourceModifyResponseIEs__value_PR_PDUSessionResourceFailedToModifyListModRes 3
#define NGAP_PDUSessionResourceModifyResponseIEs__value_PR_CriticalityDiagnostics 4
#define NGAP_PDUSessionResourceReleaseCommandIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceReleaseCommandIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PDUSessionResourceReleaseCommandIEs__value_PR_NAS_PDU 2
#define NGAP_PDUSessionResourceReleaseCommandIEs__value_PR_PDUSessionResourceToReleaseListRelCmd 3
#define NGAP_PDUSessionResourceReleaseResponseIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceReleaseResponseIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PDUSessionResourceReleaseResponseIEs__value_PR_PDUSessionResourceReleasedListRelRes 2
#define NGAP_InitialContextSetupFailureIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_InitialContextSetupFailureIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_InitialContextSetupFailureIEs__value_PR_Cause 2
#define NGAP_InitialContextSetupFailureIEs__value_PR_CriticalityDiagnostics 3
#define NGAP_UERadioCapabilityInfoIndicationIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_UERadioCapabilityInfoIndicationIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_UERadioCapabilityInfoIndicationIEs__value_PR_UERadioCapability 2
#define NGAP_NASNonDeliveryIndication_IEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_NASNonDeliveryIndication_IEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_NASNonDeliveryIndication_IEs__value_PR_NAS_PDU 2
#define NGAP_NASNonDeliveryIndication_IEs__value_PR_Cause 3
#define NGAP_OverloadStartIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_OverloadStartIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_OverloadStartIEs__value_PR_Cause 2
#define NGAP_OverloadStopIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_OverloadStopIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_OverloadStopIEs__value_PR_Cause 2
#define NGAP_UEContextModificationRequestIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_UEContextModificationRequestIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_UEContextModificationRequestIEs__value_PR_Cause 2
#define NGAP_UEContextModificationResponseIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_UEContextModificationResponseIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_UEContextModificationResponseIEs__value_PR_Cause 2
#define NGAP_PDUSessionResourceNotifyIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceNotifyIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_InitialUEMessage_IEs__value_PR_FiveG_S_TMSI 4
#define NGAP_InitialUEMessage_IEs__value_PR_UEContextRequest 5
#define NGAP_PDUSessionResourceSetupUnsuccessfulTransferIEs__value_PR_AMF_UE_NGAP_ID 0
#define NGAP_PDUSessionResourceSetupUnsuccessfulTransferIEs__value_PR_RAN_UE_NGAP_ID 1
#define NGAP_PDUSessionResourceSetupUnsuccessfulTransferIEs__value_PR_Cause 2

/* InitiatingMessage value PR enum values */
#define NGAP_InitiatingMessage__value_PR_NGSetupRequest 0
#define NGAP_InitiatingMessage__value_PR_InitialContextSetupRequest 1
#define NGAP_InitiatingMessage__value_PR_UEContextReleaseCommand 2
#define NGAP_InitiatingMessage__value_PR_PDUSessionResourceSetupRequest 3
#define NGAP_InitiatingMessage__value_PR_PDUSessionResourceModifyRequest 4
#define NGAP_InitiatingMessage__value_PR_PDUSessionResourceReleaseCommand 5
#define NGAP_InitiatingMessage__value_PR_ErrorIndication 6
#define NGAP_InitiatingMessage__value_PR_DownlinkNASTransport 7
#define NGAP_InitiatingMessage__value_PR_InitialUEMessage 8
#define NGAP_InitiatingMessage__value_PR_UplinkNASTransport 9
#define NGAP_InitiatingMessage__value_PR_Paging 11
#define NGAP_InitiatingMessage__value_PR_PathSwitchRequest 12
#define NGAP_InitiatingMessage__value_PR_UERadioCapabilityInfoIndication 13
#define NGAP_InitiatingMessage__value_PR_OverloadStart 14
#define NGAP_InitiatingMessage__value_PR_OverloadStop 15
#define NGAP_InitiatingMessage__value_PR_NASNonDeliveryIndication 10
#define NGAP_InitiatingMessage__value_PR_PDUSessionResourceModifyIndication 16
#define NGAP_InitiatingMessage__value_PR_PDUSessionResourceNotify 17
#define NGAP_InitiatingMessage__value_PR_UEContextModificationRequest 18

#define NGAP_InitiatingMessage__value_PR_UEContextReleaseRequest 19
/* SuccessfulOutcome value PR enum values */
#define NGAP_SuccessfulOutcome__value_PR_NGSetupResponse 0
#define NGAP_SuccessfulOutcome__value_PR_InitialContextSetupResponse 1
#define NGAP_SuccessfulOutcome__value_PR_UEContextReleaseComplete 2
#define NGAP_SuccessfulOutcome__value_PR_PDUSessionResourceSetupResponse 3
#define NGAP_SuccessfulOutcome__value_PR_PDUSessionResourceModifyResponse 4
#define NGAP_SuccessfulOutcome__value_PR_PDUSessionResourceReleaseResponse 5
#define NGAP_SuccessfulOutcome__value_PR_PDUSessionResourceSetupUnsuccessfulTransfer 6
#define NGAP_SuccessfulOutcome__value_PR_UEContextModificationResponse 9

/* UnsuccessfulOutcome value PR enum values */
#define NGAP_UnsuccessfulOutcome__value_PR_NGSetupFailure 0
#define NGAP_UnsuccessfulOutcome__value_PR_InitialContextSetupFailure 1
#define NGAP_UnsuccessfulOutcome__value_PR_UEContextModificationFailure 2

/* IE-specific PR enum aliases.
 * The generated asn1c headers define these PR enums correctly (e.g.
 * NGAP_Cause_PR_radioNetwork = 1 in NGAP_Cause.h). We must NOT redefine
 * them with #define here, as that would conflict (wrong values, duplicate
 * case labels). Instead, we only provide aliases for OAI name mismatches:
 *   - OAI uses NGAP_IDs_PR_* but generated enum is NGAP_UE_NGAP_IDs_PR_*
 *   - OAI uses NGAP_PDU_PR_* but generated enum is NGAP_NGAP_PDU_PR_*
 *   - OAI has a typo NGAP_Cause_PR_choice_ExtensionS (capital S)
 */
#define NGAP_IDs_PR_NOTHING NGAP_UE_NGAP_IDs_PR_NOTHING
#define NGAP_IDs_PR_aMF_UE_NGAP_ID NGAP_UE_NGAP_IDs_PR_aMF_UE_NGAP_ID
#define NGAP_IDs_PR_uE_NGAP_ID_pair NGAP_UE_NGAP_IDs_PR_uE_NGAP_ID_pair
#define NGAP_PDU_PR_initiatingMessage NGAP_NGAP_PDU_PR_initiatingMessage
#define NGAP_PDU_PR_successfulOutcome NGAP_NGAP_PDU_PR_successfulOutcome
#define NGAP_PDU_PR_unsuccessfulOutcome NGAP_NGAP_PDU_PR_unsuccessfulOutcome
#define NGAP_Cause_PR_choice_ExtensionS NGAP_Cause_PR_choice_Extensions

/* Helper macros */
#ifndef CALLOC
#define CALLOC(n, sz) calloc((n), (sz))
#endif

/* Note: asn1cSeqAdd and asn1cSequenceAdd are defined in oai_asn1.h
 * Do not redefine them here to avoid conflicts. */

#ifdef __cplusplus
}
#endif

#endif /* NGAP_OAI_COMPAT_H */