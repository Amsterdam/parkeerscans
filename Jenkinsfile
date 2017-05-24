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
            sh "docker-compose -p test -f docker-compose.yml build && " +
               "docker-compose -p test -f docker-compose.yml run --rm ppapi bash docker-test.sh"
	}, {
            sh "docker-compose -p test -f docker-compose.yml down"
        }
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
            def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking_kibanawegdeel:${env.BUILD_NUMBER}", "kibanawegdeel")
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

    stage("Build develop api/python") {
            tryStep "build", {
                def image = docker.build("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}", "api")
                image.push()
                image.push("acceptance")
            }
    }

String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                def image = docker.image("build.datapunt.amsterdam.nl:5000/datapunt/predictive_parking:${env.BUILD_NUMBER}")
                image.pull()
                image.push("acceptance")
            }
        }
    }
    stage("Deploy to ACC") {
        tryStep "deployment", {
            build job: 'Subtask_Openstack_Playbook',
                    parameters: [
                            [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                            [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-predictive-parking.yml'],
                    ]
        }
    }
}
}
