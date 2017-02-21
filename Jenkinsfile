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

    stage("Build develop kibana") {
        tryStep "build", {
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_kibana:${env.BUILD_NUMBER}", "kibana")
            image.push()
            image.push("acceptance")
        }
    }

    stage("Build develop kibana wegdeel") {
        tryStep "build", {
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_kibana:${env.BUILD_NUMBER}", "-f kibana/Dockerfile-wegdeel")
            image.push()
            image.push("acceptance")
        }
    }

    stage("Build develop logstash") {
        tryStep "build", {
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_logstash:${env.BUILD_NUMBER}", "logstash")
            image.push()
            image.push("acceptance")
        }
    }

    stage("Build develop csvimporter") {
        tryStep "build", {
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_csvpgvoer:${env.BUILD_NUMBER}", "csvimporter")
            image.push()
            image.push("acceptance")
        }
    }

    stage("Build develop web/python") {
            tryStep "build", {
                def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}", "web")
                image.push()
                image.push("acceptance")
            }
    }

    stage("Deploy to ACC") {
        tryStep "deployment", {
            build job: 'Subtask_Openstack_Playbook',
                    parameters: [
                            [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                            [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-predictive-parking.yml'],
                            [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
                    ]
        }
    }
}    //TODO tests!!
