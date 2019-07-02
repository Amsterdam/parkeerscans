#!groovy

String KIBANA_IMAGE_NAME = "datapunt/parkeerscans_kibana"
String CSVIMPORTER_IMAGE_NAME = "datapunt/parkeerscans_csvpgvoer"
String PPAPI_IMAGE_NAME = "datapunt/parkeerscans"
String DEPLOY_IMAGE_NAME = "datapunt/parkeerscans_deploy"

String DOCKER_REPOSITORY = "https://repo.data.amsterdam.nl"
String BRANCH = "${env.BRANCH_NAME}"

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
            sh "docker-compose -p pp_test -f docker-compose-test.yml down"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            docker.withRegistry("${DOCKER_REPOSITORY}",'docker-registry') {
                def kibana = docker.build("${KIBANA_IMAGE_NAME}:${env.BUILD_NUMBER}",
                    "--pull " +
                    "kibana"
                )
                kibana.push()

                def csvimporter = docker.build("${CSVIMPORTER_IMAGE_NAME}:${env.BUILD_NUMBER}",
                    "--pull " +
                    "csvimporter"
                )
                csvimporter.push()

                def ppapi = docker.build("${PPAPI_IMAGE_NAME}:${env.BUILD_NUMBER}",
                    "--pull " +
                    "api"
                )
                ppapi.push()

                def deploy = docker.build("${DEPLOY_IMAGE_NAME}:${env.BUILD_NUMBER}",
                    "--pull " +
                    "deploy"
                )
                deploy.push()
            }
        }
    }
}

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry("${DOCKER_REPOSITORY}",'docker-registry') {

                    def kibana = docker.image("${KIBANA_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    kibana.pull()
                    kibana.push("acceptance")

                    def ppapi = docker.image("${PPAPI_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    ppapi.pull()
                    ppapi.push("acceptance")

                    def csvimporter = docker.image("${CSVIMPORTER_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    csvimporter.pull()
                    csvimporter.push("acceptance")

                    def deploy = docker.image("${DEPLOY_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    deploy.pull()
                    deploy.push("acceptance")
                }
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
                docker.withRegistry("${DOCKER_REPOSITORY}",'docker-registry') {

                    def kibana = docker.image("${KIBANA_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    kibana.pull()
                    kibana.push("production")
                    kibana.push("latest")

                    def csvimporter = docker.image("${CSVIMPORTER_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    csvimporter.pull()
                    csvimporter.push("production")
                    csvimporter.push("latest")

                    def ppapi = docker.image("${PPAPI_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    ppapi.pull()
                    ppapi.push("production")
                    ppapi.push("latest")

                    def deploy = docker.image("${DEPLOY_IMAGE_NAME}:${env.BUILD_NUMBER}")
                    deploy.pull()
                    deploy.push("production")
                    deploy.push("latest")
                }
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
