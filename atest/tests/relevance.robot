*** Settings ***
Documentation    Relevance audit of the directory. Verdict is created by an AI agent. Assertions are done by the
...              test cases.
...
...              The test case below is a test template: the TestCaseGenerator pre-run modifier multiplies it once
...              per Markdown file under content/directory/, binding ${resource} in each copy.
...
...              Needs AGENT_API_KEY. Without it, every test is skipped rather than failed.

Library          Collections
Resource         ${CURDIR}/../resources/relevance.resource


*** Test Cases ***
Test Resource ${resource}
    [Documentation]    Audits one directory resource.
    [Tags]    robot:continue-on-failure

    Should Topic Be On Software Testing Or Quality    ${resource}

    Should Language Be French    ${resource}

    IF    $resource.paid
        Should Be Paid Resource    ${resource}
    ELSE
        Should Be Free Resource    ${resource}
    END

    IF    $resource.category == 'livres'
        Resource Status Should Be '${resource.status}'    ${resource}
    END

    ${tags_found}=    Get Actual Resource Categories    ${resource}
    List Should Contain Sub List    ${tags_found}    ${resource.tags}


*** Keywords ***
Resource Status Should Be '${status}'
    [Documentation]    Assert the actual activity of a resource. LinkedIn resource can't be defined with accuracy.
    [Arguments]    ${resource}

    TRY
        IF    $status == 'Active'
            Should Be Active    ${resource}
        ELSE IF    $status == 'Inactive'
            Should Not Be Active    ${resource}
        ELSE IF    $status == 'Closed'
            Should Be Discontinued    ${resource}
        ELSE
            Log    Status unknown '${status}'    level=WARN
        END
    EXCEPT    AS    ${error}
        IF    "linkedin" in $resource.link
            Log    Skip status verification: cannot evaluate with accuracy LinkedIn resource\nError: ${error}
            RETURN
        END
        Fail    ${error}
    END
