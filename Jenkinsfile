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

    stage("Test") {
        tryStep "Test", {
            sh "./deploy_test.sh"
	}, {
            sh "docker-compose -p test -f docker-compose-test.yml down"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            def kibana = docker.build("repo.data.amsterdam.nl/datapunt/parkeerscans_kibana:${env.BUILD_NUMBER}", "kibana")
            kibana.push()
            kibana.push("acceptance")

            def csvimporter = docker.build("repo.data.amsterdam.nl/datapunt/parkeerscans_csvpgvoer:${env.BUILD_NUMBER}", "csvimporter")
            csvimporter.push()
            csvimporter.push("acceptance")

            def ppapi = docker.build("repo.data.amsterdam.nl/datapunt/parkeerscans:${env.BUILD_NUMBER}", "api")
            ppapi.push()
            ppapi.push("acceptance")
        }
    }
}

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                def image = docker.image("repo.data.amsterdam.nl/datapunt/parkeerscans:${env.BUILD_NUMBER}")
                image.pull()
                image.push("acceptance")
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-parkeerscans.yml'],
                ]
            }
        }
    }


    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'Parkeerscans is waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                def kibana = docker.image("repo.data.amsterdam.nl/datapunt/parkeerscans_kibana:${env.BUILD_NUMBER}")
                kibana.pull()
                kibana.push("production")
                kibana.push("latest")

                def csvimporter = docker.image("repo.data.amsterdam.nl/datapunt/parkeerscans_csvpgvoer:${env.BUILD_NUMBER}")
                csvimporter.pull()
                csvimporter.push("production")
                csvimporter.push("latest")

                def ppapi = docker.image("repo.data.amsterdam.nl/datapunt/parkeerscans:${env.BUILD_NUMBER}")
                ppapi.pull()
                ppapi.push("production")
                ppapi.push("latest")
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-parkeerscans.yml'],
                ]
            }
        }
    }
}
