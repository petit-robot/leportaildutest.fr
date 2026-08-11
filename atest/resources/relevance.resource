*** Settings ***
Documentation       Keywords asserting that a resource still matches what it declares.
...
...                 Every assertion reads the same verdict, obtained once per resource from the AI agent.
...                 Keywords interprets the verdict returned by the agent.

Library             Collections
Library             DateTime
Library             String
Library             ${CURDIR}/../libs/RelevanceAuditAgent.py    model=${MODEL}    agent_id=${AGENT_ID}


*** Variables ***
${MODEL}        mistral-large-latest
${AGENT_ID}     ${None}    # To pass at execution else a new agent will be created.


*** Keywords ***
Should Topic Be On Software Testing Or Quality
    [Documentation]    Fail unless the resource is about software testing or quality engineering.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${message}=    Create Error Message
    ...    ${resource}    topic    not about software testing or quality    ${verdict}[topic_reason]
    Should Be True    $verdict['topic_ok']    msg=${message}

Should Language Be French
    [Documentation]    Fail unless the resource publishes in French.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${code}=    Convert To Lower Case    ${verdict}[language_code]
    ${found}=    Get Substring    ${code.strip()}    0    2
    ${language}=    Set Variable If    $found    '${found}'    an unknown language
    ${message}=    Create Error Message
    ...    ${resource}    language    published in ${language}, expected 'fr'    ${verdict}[language_reason]
    Should Be Equal    ${found}    fr    msg=${message}    values=${False}

Should Be Paid Resource
    [Documentation]    Fail unless reaching the content costs money. A free account is not a payment.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${message}=    Create Error Message
    ...    ${resource}    pricing    declared paid but looks freely accessible    ${verdict}[pricing_reason]
    Should Be True    $verdict['is_paid']    msg=${message}

Should Be Free Resource
    [Documentation]    Fail unless the content is reachable without paying.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${message}=    Create Error Message
    ...    ${resource}    pricing    declared free but reaching the content requires paying
    ...    ${verdict}[pricing_reason]
    Should Not Be True    $verdict['is_paid']    msg=${message}

Should Activity Earlier Than '${duration}'
    [Documentation]    Fail unless the resource published something within `duration`.
    ...
    ...    A resource nothing could date falls back on `is_active`: the agent can see
    ...    a resource is still running without being able to date what it publishes.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${date_published}=    Convert Date    ${verdict}[last_publication]
    ${date_limit}=    Get Current Date    increment=-${duration}
    ${message}=    Create Error Message
    ...    ${resource}    activity
    ...    declared active but last published ${date_published}, before the ${date_limit} limit
    ...    ${verdict}[activity_reason]
    Should Be True    $date_published >= $date_limit    msg=${message}

Should Activity Older Than '${duration}'
    [Documentation]    Fail unless the resource has published nothing for `duration`.
    ...
    ...    A resource nothing could date falls back on `is_active`, the same way
    ...    `Should Activity Earlier Than` does.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${date_published}=    Convert Date    ${verdict}[last_publication]
    ${date_limit}=    Get Current Date    increment=-${duration}
    ${message}=    Create Error Message
    ...    ${resource}    activity
    ...    declared inactive but published ${date_published}, after the ${date_limit} limit
    ...    ${verdict}[activity_reason]
    Should Be True    $date_published < $date_limit    msg=${message}

Should Be Active
    [Documentation]    Fail unless the resource is still running.
    ...
    ...    Judged on signs of life rather than on a date, so a resource the agent
    ...    could not date is still answered for.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    IF    $verdict["last_publication"] == "unknown"
        ${message}=    Create Error Message
        ...    ${resource}    activity    declared active but the resource shows no sign of life
        ...    ${verdict}[activity_reason]
        Should Be True    $verdict['is_active']    msg=${message}
    ELSE
        Should Activity Earlier Than '104 weeks'    ${resource}
    END

Should Not Be Active
    [Documentation]    Fail unless the resource has stopped running, closed or not.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    IF    $verdict["last_publication"] == "unknown"
        ${message}=    Create Error Message
        ...    ${resource}    activity    declared inactive but the resource is still running
        ...    ${verdict}[activity_reason]
        Should Not Be True    $verdict['is_active']    msg=${message}
    ELSE
        Should Activity Older Than '104 weeks'    ${resource}
    END

Should Be Discontinued
    [Documentation]    Fail unless the resource is gone, or announces it has stopped for good.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${message}=    Create Error Message
    ...    ${resource}    activity    declared closed but the resource is still around
    ...    ${verdict}[activity_reason]
    Should Be True    $verdict['is_discontinued']    msg=${message}

Get Actual Resource Categories
    [Documentation]    The categories the agent attributes to the resource, judged blind.
    ...
    ...    Anything the agent invents outside the site's own vocabulary is dropped:
    ...    a category the site does not offer cannot be missing from a frontmatter.
    [Arguments]    ${resource}
    ${verdict}=    Get Resource Verdict    ${resource}
    ${allowed}=    Get Resource Categories
    VAR    @{tags}=    @{EMPTY}
    FOR    ${tag}    IN    @{verdict}[tags]
        IF    $tag in $allowed
            Append To List    ${tags}    ${tag}
        ELSE
            Log    Not allowed category: ${tag}    level=WARN
        END
    END
    RETURN    ${tags}

Create Error Message
    [Documentation]    The failure message for `criterion`, quoting the agent and whatever it cited.
    [Arguments]    ${resource}    ${criterion}    ${summary}    ${reason}
    ${message}=    Catenate    SEPARATOR=\n
    ...    ${resource.identifier} [${criterion}]: ${summary}
    ...    Agent: ${reason}
    RETURN    ${message}
