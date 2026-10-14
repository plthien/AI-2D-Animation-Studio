export interface paths {
    "/api/v1/channels": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Channels */
        get: operations["list_channels_api_v1_channels_get"];
        put?: never;
        /** Create Channel */
        post: operations["create_channel_api_v1_channels_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/channels/{channel_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Channel */
        get: operations["get_channel_api_v1_channels__channel_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/channels/{channel_id}/dna": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Channel Dna */
        get: operations["get_channel_dna_api_v1_channels__channel_id__dna_get"];
        /** Update Channel Dna */
        put: operations["update_channel_dna_api_v1_channels__channel_id__dna_put"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/jobs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Jobs */
        get: operations["list_jobs_api_v1_jobs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/jobs/{job_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Job */
        get: operations["get_job_api_v1_jobs__job_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/projects": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Projects */
        get: operations["list_projects_api_v1_projects_get"];
        put?: never;
        /** Create Project */
        post: operations["create_project_api_v1_projects_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/projects/{project_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Project */
        get: operations["get_project_api_v1_projects__project_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/projects/{project_id}/artifacts": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Project Artifacts */
        get: operations["list_project_artifacts_api_v1_projects__project_id__artifacts_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/projects/{project_id}/heads": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Project Heads */
        get: operations["get_project_heads_api_v1_projects__project_id__heads_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health */
        get: operations["health_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** ArtifactResponse */
        ArtifactResponse: {
            /** Artifact Id */
            artifact_id: string;
            /** Created At */
            created_at: string;
            /** Kind */
            kind: string;
            /** Logical Key */
            logical_key: string;
            /** Sha256 */
            sha256: string;
            /** Size Bytes */
            size_bytes: number;
            /** Status */
            status: string;
            /** Version */
            version: number;
        };
        /** ChannelCreate */
        ChannelCreate: {
            /** Audience */
            audience: string;
            /** Language */
            language: string;
            /** Name */
            name: string;
            /** Niche */
            niche: string;
        };
        /** ChannelDNAResponse */
        ChannelDNAResponse: {
            /** Artifact Id */
            artifact_id: string | null;
            /** Dna */
            dna: {
                [key: string]: components["schemas"]["JsonValue"];
            } | null;
            /** Narration Identity Hash */
            narration_identity_hash: string | null;
            /** Performance Style Hash */
            performance_style_hash: string | null;
            /** Visual Style Hash */
            visual_style_hash: string | null;
        };
        /** ChannelDNAUpdate */
        ChannelDNAUpdate: {
            /** Dna */
            dna: {
                [key: string]: components["schemas"]["JsonValue"];
            };
            /** Expected Current Artifact Id */
            expected_current_artifact_id: string | null;
        };
        /** ChannelResponse */
        ChannelResponse: {
            /** Audience */
            audience: string;
            /** Channel Id */
            channel_id: string;
            /** Created At */
            created_at: string;
            /** Language */
            language: string;
            /** Name */
            name: string;
            /** Niche */
            niche: string;
            /** Updated At */
            updated_at: string;
        };
        /** DataEnvelope[ChannelDNAResponse] */
        DataEnvelope_ChannelDNAResponse_: {
            data: components["schemas"]["ChannelDNAResponse"];
        };
        /** DataEnvelope[ChannelResponse] */
        DataEnvelope_ChannelResponse_: {
            data: components["schemas"]["ChannelResponse"];
        };
        /** DataEnvelope[HealthResponse] */
        DataEnvelope_HealthResponse_: {
            data: components["schemas"]["HealthResponse"];
        };
        /** DataEnvelope[JobResponse] */
        DataEnvelope_JobResponse_: {
            data: components["schemas"]["JobResponse"];
        };
        /** DataEnvelope[PageResponse[ArtifactResponse]] */
        DataEnvelope_PageResponse_ArtifactResponse__: {
            data: components["schemas"]["PageResponse_ArtifactResponse_"];
        };
        /** DataEnvelope[PageResponse[ChannelResponse]] */
        DataEnvelope_PageResponse_ChannelResponse__: {
            data: components["schemas"]["PageResponse_ChannelResponse_"];
        };
        /** DataEnvelope[PageResponse[JobResponse]] */
        DataEnvelope_PageResponse_JobResponse__: {
            data: components["schemas"]["PageResponse_JobResponse_"];
        };
        /** DataEnvelope[PageResponse[ProjectResponse]] */
        DataEnvelope_PageResponse_ProjectResponse__: {
            data: components["schemas"]["PageResponse_ProjectResponse_"];
        };
        /** DataEnvelope[ProjectHeadsResponse] */
        DataEnvelope_ProjectHeadsResponse_: {
            data: components["schemas"]["ProjectHeadsResponse"];
        };
        /** DataEnvelope[ProjectResponse] */
        DataEnvelope_ProjectResponse_: {
            data: components["schemas"]["ProjectResponse"];
        };
        /** ErrorBody */
        ErrorBody: {
            /** Code */
            code: string;
            /** Details */
            details: {
                [key: string]: components["schemas"]["JsonValue"];
            };
            /** Message */
            message: string;
            /** Retryable */
            retryable: boolean;
        };
        /** ErrorEnvelope */
        ErrorEnvelope: {
            error: components["schemas"]["ErrorBody"];
        };
        /** HealthResponse */
        HealthResponse: {
            /** Schema Version */
            schema_version: string;
            /** Status */
            status: string;
        };
        /** JobResponse */
        JobResponse: {
            /** Created At */
            created_at: string;
            /** Heartbeat At */
            heartbeat_at: string | null;
            /** Job Id */
            job_id: string;
            /** Kind */
            kind: string;
            /** Operation Id */
            operation_id: string | null;
            /** Progress */
            progress: number;
            /** Project Id */
            project_id: string;
            /** Status */
            status: string;
            /** Updated At */
            updated_at: string;
        };
        JsonValue: unknown;
        /** PageResponse[ArtifactResponse] */
        PageResponse_ArtifactResponse_: {
            /** Items */
            items: components["schemas"]["ArtifactResponse"][];
            /** Page */
            page: number;
            /** Page Size */
            page_size: number;
            /** Total */
            total: number;
        };
        /** PageResponse[ChannelResponse] */
        PageResponse_ChannelResponse_: {
            /** Items */
            items: components["schemas"]["ChannelResponse"][];
            /** Page */
            page: number;
            /** Page Size */
            page_size: number;
            /** Total */
            total: number;
        };
        /** PageResponse[JobResponse] */
        PageResponse_JobResponse_: {
            /** Items */
            items: components["schemas"]["JobResponse"][];
            /** Page */
            page: number;
            /** Page Size */
            page_size: number;
            /** Total */
            total: number;
        };
        /** PageResponse[ProjectResponse] */
        PageResponse_ProjectResponse_: {
            /** Items */
            items: components["schemas"]["ProjectResponse"][];
            /** Page */
            page: number;
            /** Page Size */
            page_size: number;
            /** Total */
            total: number;
        };
        /** ProjectCreate */
        ProjectCreate: {
            /** Channel Id */
            channel_id: string;
            /**
             * Description
             * @default
             */
            description: string;
            /** Name */
            name: string;
        };
        /** ProjectHeadsResponse */
        ProjectHeadsResponse: {
            /** Items */
            items: components["schemas"]["StageHeadResponse"][];
            /** Stages */
            stages: components["schemas"]["StageResponse"][];
        };
        /** ProjectResponse */
        ProjectResponse: {
            /** Channel Id */
            channel_id: string;
            /** Created At */
            created_at: string;
            /** Description */
            description: string;
            /** Name */
            name: string;
            /** Project Id */
            project_id: string;
            /** Stages */
            stages?: components["schemas"]["StageResponse"][] | null;
            /** Status */
            status: string;
            /** Updated At */
            updated_at: string;
        };
        /** StageHeadResponse */
        StageHeadResponse: {
            /** Approval Status */
            approval_status: string;
            /** Artifact Id */
            artifact_id: string;
            /** Stage Key */
            stage_key: string;
            /** Updated At */
            updated_at: string;
        };
        /** StageResponse */
        StageResponse: {
            /** Artifact Id */
            artifact_id: string | null;
            /** Blocked Reason */
            blocked_reason: string | null;
            /** Label */
            label: string;
            /** Stage Key */
            stage_key: string;
            /** Status */
            status: string;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    list_channels_api_v1_channels_get: {
        parameters: {
            query?: {
                page?: number;
                page_size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_PageResponse_ChannelResponse__"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    create_channel_api_v1_channels_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChannelCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_ChannelResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    get_channel_api_v1_channels__channel_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                channel_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_ChannelResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    get_channel_dna_api_v1_channels__channel_id__dna_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                channel_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_ChannelDNAResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    update_channel_dna_api_v1_channels__channel_id__dna_put: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                channel_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ChannelDNAUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_ChannelDNAResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    list_jobs_api_v1_jobs_get: {
        parameters: {
            query?: {
                project_id?: string | null;
                page?: number;
                page_size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_PageResponse_JobResponse__"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    get_job_api_v1_jobs__job_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                job_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_JobResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    list_projects_api_v1_projects_get: {
        parameters: {
            query?: {
                channel_id?: string | null;
                page?: number;
                page_size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_PageResponse_ProjectResponse__"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    create_project_api_v1_projects_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ProjectCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_ProjectResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    get_project_api_v1_projects__project_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                project_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_ProjectResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    list_project_artifacts_api_v1_projects__project_id__artifacts_get: {
        parameters: {
            query?: {
                kind?: string | null;
                page?: number;
                page_size?: number;
            };
            header?: never;
            path: {
                project_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_PageResponse_ArtifactResponse__"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    get_project_heads_api_v1_projects__project_id__heads_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                project_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_ProjectHeadsResponse_"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorEnvelope"];
                };
            };
        };
    };
    health_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DataEnvelope_HealthResponse_"];
                };
            };
        };
    };
}
