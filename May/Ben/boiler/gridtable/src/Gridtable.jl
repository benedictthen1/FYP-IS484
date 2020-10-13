
module Gridtable
using Dash

const resources_path = realpath(joinpath( @__DIR__, "..", "deps"))
const version = "0.0.1"

include("''_gridtable.jl")

function __init__()
    DashBase.register_package(
        DashBase.ResourcePkg(
            "gridtable",
            resources_path,
            version = version,
            [
                DashBase.Resource(
    relative_package_path = "gridtable.min.js",
    external_url = "https://unpkg.com/gridtable@0.0.1/gridtable/gridtable.min.js",
    dynamic = nothing,
    async = nothing,
    type = :js
),
DashBase.Resource(
    relative_package_path = "gridtable.min.js.map",
    external_url = "https://unpkg.com/gridtable@0.0.1/gridtable/gridtable.min.js.map",
    dynamic = true,
    async = nothing,
    type = :js
)
            ]
        )

    )
end
end
