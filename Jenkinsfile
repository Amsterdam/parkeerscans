#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage("Checkout") {
        checkout scm
    }

    stage("Build develop logstash image") {
        tryStep "build", {
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_logstash:${env.BUILD_NUMBER}", "logstash")
            image.push()
            image.push("acceptance")
        }
    }

    stage("Build develop image") {
            tryStep "build", {
                def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}")
                image.push()
                image.push("acceptance")
            }
        }
}

--String BRANCH = "${env.BRANCH_NAME}"
--
--if (BRANCH == "master") {
--
--
--node {
--    stage("Deploy to ACC") {
--        tryStep "deployment", {
--            build job: 'Subtask_Openstack_Playbook',
--                    parameters: [
--                            [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
--                            [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-predictive-parking.yml'],
--                            [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
--                    ]
--        }
--    }
--}


--stage('Waiting for approval') {
--    slackSend channel: '#ci-channel', color: 'warning', message: 'NAP meetbouten is waiting for Production Release - please confirm'
--    input "Deploy to Production?"
--}
--
--node {
--    stage('Push production image logstash') {
--        tryStep "image tagging", {
--            def image = docker.image("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_logstash:${env.BUILD_NUMBER}")
--            image.pull()
--
--            image.push("production")
--            image.push("latest")
--        }
--    }
--}


--node {
--    stage('Push production image') {
--        tryStep "image tagging", {
--            def image = docker.image("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}")
--            image.pull()
--
--            image.push("production")
--            image.push("latest")
--        }
--    }
--}

--node {
--    stage("Deploy") {
--        tryStep "deployment", {
--            build job: 'Subtask_Openstack_Playbook',
--                    parameters: [
--                            [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
--                            [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-predictive-parking.yml'],
--                                [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
--                    ]
--            }
--        }
--    }
}